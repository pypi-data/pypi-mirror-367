import string
import random
from functools import wraps
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Any, List
import polars as pl
import inflection
from pydantic import BaseModel, computed_field, field_validator

PolarsDataFrame = TypeVar("polars.dataframe.frame.DataFrame")
PolarsLazyFrame = TypeVar("polars.lazyframe.frame.LazyFrame")


def completion(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        def complete_task(self_in):
            self_in.complete_input_tasks()
            print(
                f"Starting completion of {self_in.task_name} with id {self_in.task_id}"
            )
            self_in.validate_min_inputs_schemas()
            func(*args, **kwargs)
            if (
                self_in.cache
                and hasattr(self_in, "cache_type")
                and self_in.cache_type == "std"
            ):
                self_in.env_vars["query_conn"].cache_write_func(
                    self_in.output, self_in.cache_local
                )

        self_in = args[0]
        self_in.set_anchor_cohort()
        if hasattr(self_in, "cache") and self_in.cache and len(self_in.inputs) == 0:
            res = self_in.env_vars["query_conn"].get_cache(
                local=self_in.cache_local, lazy=self_in.lazy
            )
            if res is not None:
                self_in.output = res
                print(f"{self_in.task_name} is cached from {self_in.cache_local}")
            else:
                complete_task(self_in)
        else:
            complete_task(self_in)
        self_in.set_output_dtypes_and_names()
        self_in.filter_required_cols()
        if "anchor" in list(self_in.inputs.keys()):
            self_in.anchor_data()
        if "anchor" in list(self_in.input_tasks.keys()):
            self_in.input_tasks["anchor"].anchored_data.append(self_in)
        self_in.complete_date_aggregate()
        self_in.validate_min_output_schema()
        self_in.output = self_in.output.unique()
        self_in.completed = True

    return wrapper


class Task(BaseModel, ABC):
    """Generic task class representing one step in analysis."""

    #: task id
    task_id: str = None

    #: input dataframes
    inputs: dict = {}

    #: input tasks
    input_tasks: dict = {}

    #: minimum requirements on inputs schema to avoid any errors
    min_inputs_schemas: Optional[dict[str, dict]] = {}

    #: minimum requirements on output schema
    min_output_schema: Optional[dict[str, str]] = {}

    #: environment variables applied to each task in analysis plan
    env_vars: Optional[dict[str, Any]] = {}

    #: task variables specific to each task
    task_vars: Optional[dict[str, Any]] = {}

    #: output of complete method representing result of task
    output: PolarsDataFrame | PolarsLazyFrame = None

    #: either the task is completed
    completed: bool = False

    aggregate: str = "all"

    date_col: str = "date"

    person_col: str = "person_id"

    val_col: str = "value"

    required_cols: List[str] = ["person_id"]

    anchor_date: str = None

    anchor_range: List[str | int | None] = [None, None]

    anchor_pid: str = None

    anchored_data: List[Any] = []

    @field_validator("inputs", mode="after")
    @classmethod
    def validate_task_inputs(cls, inputs: dict) -> dict:
        if not isinstance(inputs, dict):
            raise ValueError("inputs must be None or a dictionary")
        elif not all([isinstance(k, str) for k in list(inputs.keys())]):
            raise ValueError("all keys of inputs dictionary must be strings")
        elif not (
            all([isinstance(v, pl.DataFrame) for v in list(inputs.values())])
            or all([isinstance(v, pl.LazyFrame) for v in list(inputs.values())])
        ):
            raise ValueError(
                "all values of inputs dictionary must be polars dataframe or polars lazyframe"
            )
        return inputs

    @computed_field
    @property
    def task_name(self) -> str:
        return inflection.underscore(self.__class__.__name__)

    def model_post_init(self, __context__=None):
        if self.task_id is None:
            self.task_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )

    def validate_min_inputs_schemas(self):
        print("Validating the inputs...")
        for k in self.min_inputs_schemas.keys():
            sc = self.inputs[k].collect_schema().to_python()
            try:
                if dict(sc, **self.min_inputs_schemas[k]) != sc:
                    raise ValueError("minimal inputs schemas are not satisfied!")
            except KeyError:
                raise ValueError("missing input dataframe")
        return True

    def validate_min_output_schema(self):
        print("Validating the output...")
        sc = self.output.collect_schema().to_python()
        if dict(sc, **self.min_output_schema) != sc:
            raise ValueError("minimal output schemas are not satisfied!")
        return True

    class Config:
        validate_assignment = True

    def complete_input_tasks(self):
        for task in self.input_tasks.values():
            if not task.completed:
                task.complete()
        self.inputs.update(**{k: v.output for k, v in self.input_tasks.items()})

    @abstractmethod
    def complete(self):
        pass

    def set_date_column_dtype(self, date_col: str = None):
        if date_col is None:
            date_col = self.date_col
        if isinstance(self.output.collect_schema().get(date_col), pl.String):
            self.output = self.output.with_columns(pl.col(date_col).str.to_date())

    def filter_required_cols(self):
        self.output = self.output.drop_nulls(self.required_cols)

    def set_output_dtypes_and_names(self):
        pass

    def value_aggregate_min(self, by):
        self.output = self.output.group_by(*by).agg(pl.col(self.val_col).min())

    def value_aggregate_max(self, by):
        self.output = self.output.group_by(*by).agg(pl.col(self.val_col).max())

    def value_aggregate_quant(self, by, quant):
        self.output = self.output.group_by(*by).agg(
            pl.col(self.val_col).quantile(quant)
        )

    def date_aggregate_closest(self):
        self.output = (
            self.output.with_column(
                (pl.col(self.date) - pl.col("anchor_date"))
                .dt.total_days()
                .abs()
                .alias("tte")
            )
            .group_by(self.person_col, "anchor_date", maintain_order=True)
            .agg(pl.all().bottom_k_by("tte", 1))
            .explode(pl.all().exclude(self.person_col, "anchor_date"))
        ).drop("tte")

    def date_aggregate_first(self, by):
        self.output = (
            self.output.group_by(*by, maintain_order=True)
            .agg(pl.all().bottom_k_by(self.date_col, 1))
            .explode(pl.all().exclude(*by))
        )

    def date_aggregate_last(self, by):
        self.output = (
            self.output.group_by(*by, maintain_order=True)
            .agg(pl.all().top_k_by(self.date_col, 1))
            .explode(pl.all().exclude(*by))
        )

    def complete_date_aggregate(self):
        if "anchor_date" in self.output.columns:
            by_cols = [self.person_col, "anchor_date"]
        else:
            by_cols = [self.person_col]
        if self.aggregate.find("quantile") == 0:
            self.value_aggregate_quant(
                by=by_cols, quant=float(self.aggregate.replace("quantile:", "")) / 100
            )
        match self.aggregate:
            case "all":
                return None
            case "closest":
                self.date_aggregate_closest()
            case "first":
                self.date_aggregate_first(by=by_cols)
            case "last":
                self.date_aggregate_last(by=by_cols)
            case "min":
                self.value_aggregate_min(by=by_cols)
            case "max":
                self.value_aggregate_max(by=by_cols)

    def anchor_data(self):
        predicates = [pl.col(self.person_col) == pl.col(f"{self.anchor_pid}_right")]
        time_range_cols = {}
        if self.anchor_range[0] is None and self.anchor_range[1] is None:
            self.output = self.output.join(
                self.inputs["anchor"]
                .select(self.anchor_pid)
                .rename({self.anchor_pid: f"{self.anchor_pid}_right"}),
                left_on=self.person_col,
                right_on=f"{self.anchor_pid}_right",
                coalesce=False,
            )
            self.output = self.output.rename({f"{self.anchor_pid}_right": "anchor_pid"})
        else:
            if self.anchor_range[0] is not None:
                predicates.append(pl.col(self.date_col) >= pl.col("date_range_start"))
                if isinstance(self.anchor_range[0], str):
                    time_range_cols["date_range_start"] = pl.col(self.anchor_range[0])
                elif isinstance(self.anchor_range[0], int):
                    time_range_cols["date_range_start"] = pl.col(
                        self.anchor_date
                    ).dt.offset_by(f"{self.anchor_range[0]}d")

            if self.anchor_range[1] is not None:
                predicates.append(pl.col(self.date_col) <= pl.col("date_range_end"))
                if isinstance(self.anchor_range[1], str):
                    time_range_cols["date_range_end"] = pl.col(self.anchor_range[1])
                elif isinstance(self.anchor_range[1], int):
                    time_range_cols["date_range_end"] = pl.col(
                        self.anchor_date
                    ).dt.offset_by(f"{self.anchor_range[1]}d")

            self.output = self.output.join_where(
                self.inputs["anchor"]
                .with_columns(**time_range_cols)
                .select(
                    self.anchor_pid, self.anchor_date, *list(time_range_cols.keys())
                )
                .rename({self.anchor_pid: f"{self.anchor_pid}_right"}),
                *predicates,
            ).rename(
                {
                    f"{self.anchor_pid}_right": "anchor_pid",
                    self.anchor_date: "anchor_date",
                }
            )

    def set_anchor_cohort(self):
        if self.anchor_date is None and "anchor" in list(self.input_tasks.keys()):
            self.anchor_date = self.input_tasks["anchor"].date_col
        if self.anchor_pid is None and "anchor" in list(self.input_tasks.keys()):
            self.anchor_pid = self.input_tasks["anchor"].person_col

    def merge_with_anchored_data(self):
        if len(self.anchored_data) > 0:
            for ad in self.anchored_data:
                ad.merge_with_anchored_data()
                if "date_range_start" in list(ad.output.columns):
                    self.output = self.output.join(
                        ad.output.drop(
                            "date_range_start", "date_range_end", "person_id"
                        ),
                        left_on=[self.person_col, self.date_col],
                        right_on=["anchor_pid", "anchor_date"],
                        suffix="_" + ad.task_id,
                    )
                else:
                    self.output = self.output.join(
                        ad.output.drop("person_id"),
                        left_on=self.person_col,
                        right_on="anchor_pid",
                        suffix="_" + ad.task_id,
                    )
