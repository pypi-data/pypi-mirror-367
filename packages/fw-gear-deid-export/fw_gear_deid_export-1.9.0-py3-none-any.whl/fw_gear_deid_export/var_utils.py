"""Module with utilities related to handling Jinja variables."""

import logging
import os
import re
import typing as t

import flywheel
import pandas as pd
from dotty_dict import Dotty
from ruamel.yaml import YAML

KEY_TYPES = ["PUBLIC_KEY", "PRIVATE_KEY", "SECRET_KEY"]
DEFAULT_REQUIRED_COLUMNS = ["subject.label"]
DEFAULT_SUBJECT_CODE_COL = "subject.label"
DEFAULT_NEW_SUBJECT_LOC = "export.subject.label"
DEFAULT_SESSION_CODE_COL = "session.label"

log = logging.getLogger(__name__)


def get_jinja_variables(deid_template_path: os.PathLike) -> t.Tuple[list, list, list]:
    """Gets the jinja variables (`"{{ VARIABLE }}"`) and sorts by type.

    Args:
        deid_template_path: Path to deid template YAML profile

    Returns:
        list: variables to be set from Flywheel `subject` metadata
        list: variables to be set from Flywheel `session` metadata
        list: variables to be set from CSV input file
    """

    with open(deid_template_path, "r") as fid:
        deid_template_str = fid.read()
    jinja_vars = re.findall(r"{{[^{}]+}}", deid_template_str)
    jinja_vars = [v.strip("{} ") for v in jinja_vars]
    jinja_vars = [v for v in jinja_vars if v not in KEY_TYPES]
    subj_vars, sess_vars, csv_vars = [], [], []
    for v in jinja_vars:
        if v.startswith("subject."):
            subj_vars.append(v)
        elif v.startswith("session."):
            sess_vars.append(v)
        else:
            csv_vars.append(v)
    subj_vars = [v for v in set(subj_vars)]
    sess_vars = [v for v in set(sess_vars)]
    csv_vars = [v for v in set(csv_vars)]

    return subj_vars, sess_vars, csv_vars


def get_meta_df(  # noqa: PLR0912 (too many branches)
    origin: flywheel.Project | flywheel.Subject | flywheel.Session,
    subj_vars: list = [],
    sess_vars: list = [],
    session_level_profile: bool = False,
) -> pd.DataFrame:
    """Given origin container and metadata variables from profile, returns DataFrame.

    Args:
        origin: Flywheel container (Project, Subject, Session)
        subj_vars: List of Jinja variables that begin with `subject.`
        sess_vars: List of Jinja variables that begin with `session.`
        session_level_profile: Whether df will be supporting session level profiles

    Returns:
        pd.DataFrame: Metadata df with columns for subject(+session) labels and variables
    """
    if origin.container_type == "project":
        subjects = origin.subjects.find() or []
    elif origin.container_type == "subject":
        subjects = [origin]
    elif origin.container_type == "session":
        subjects = [origin.subject]
    else:
        raise ValueError(f"Invalid gear run level: {origin.container_type}")

    if session_level_profile:
        session_dfs = []
        for subject in subjects:
            sessions = subject.sessions.find() or []
            vars = subj_vars + sess_vars
            sess_df = pd.DataFrame(
                columns=vars, index=[session.label for session in sessions]
            )
            sess_df.index.name = "session.label"

            subject = subject.reload()
            dotty_subj = Dotty(subject.to_dict())
            for var in subj_vars:
                if val := dotty_subj.get(var.removeprefix("subject.")):
                    sess_df[var] = val
                else:
                    log.warning(
                        f"No value for {subject.label} {var}. Subject will be skipped."
                    )
                    sess_df[var] = None
            for session in sessions:
                session = session.reload()
                dotty_sess = Dotty(session.to_dict())
                for var in sess_vars:
                    if val := dotty_sess.get(var.removeprefix("session.")):
                        sess_df.loc[session.label, var] = val
                    else:
                        log.warning(
                            f"No value for {subject.label}/{session.label} {var}. "
                            "Session will be skipped."
                        )
                        sess_df.loc[session.label, var] = None
            sess_df.columns = sess_df.columns.str.replace(".", "_")
            sess_df["subject.label"] = subject.label
            sess_df.reset_index(inplace=True)
            # Drop incomplete rows - the above warning logs inform user what values are missing
            sess_df.dropna(inplace=True)
            session_dfs.append(sess_df)
        subj_df = pd.concat(session_dfs, ignore_index=True)

    else:
        subj_df = pd.DataFrame(
            columns=subj_vars, index=[subject.label for subject in subjects]
        )
        subj_df.index.name = "subject.label"

        for subject in subjects:
            subject = subject.reload()
            dotty_subj = Dotty(subject.to_dict())
            for var in subj_vars:
                if val := dotty_subj.get(var.removeprefix("subject.")):
                    subj_df.loc[subject.label, var] = val
                else:
                    log.warning(
                        f"No value for {subject.label} {var}. Subject will be skipped."
                    )
                    subj_df.loc[subject.label, var] = None

        subj_df.columns = subj_df.columns.str.replace(".", "_")
        subj_df.reset_index(inplace=True)
        subj_df.dropna(inplace=True)

    return subj_df


def get_csv_df(  # noqa: PLR0913
    deid_template_path: os.PathLike,
    csv_path: os.PathLike,
    subject_label_col: str = DEFAULT_SUBJECT_CODE_COL,
    new_subject_label_loc: str = DEFAULT_NEW_SUBJECT_LOC,
    session_label_col: str = DEFAULT_SESSION_CODE_COL,
    session_level_profile: bool = False,
    required_cols: t.Optional[list] = None,
    csv_vars: t.Optional[list] = [],
) -> pd.DataFrame:
    """Creates dataframe from input CSV and validates with deid_template.

    Args:
        deid_template_path: Path to deid template YAML profile
        csv_path: Path to CSV file
        subject_label_col: Subject label column name
        new_subject_label_loc: New subject location in template (dotty dict notation)
        session_label_col: Session label column name
        session_level_profile: Whether df will be supporting session level profiles
        required_cols: List of required column names
        csv_vars: List of Jinja variables found in deid template YAML profile

    Returns:
        pd.DataFrame: DataFrame of template updates according to CSV input
    """
    with open(deid_template_path, "r") as fid:
        yaml = YAML(typ="rt")
        deid_template = yaml.load(fid)

    csv_df = pd.read_csv(csv_path, dtype=str)

    # Check that all expected variables exist
    if required_cols is None:
        required_cols = [subject_label_col]
        if session_level_profile:
            required_cols.append(session_label_col)
    required_cols += csv_vars
    required_cols = set(required_cols)
    for c in required_cols:
        if c not in csv_df:
            raise ValueError(f"Column {c} is missing from dataframe")
    for c in csv_df:
        if c not in required_cols:
            log.debug(f"Column {c} not found in DeID template")

    # Check for uniqueness of subject columns
    if session_level_profile:
        if not (csv_df[["subject.label", "session.label"]].value_counts() == 1).all():
            raise ValueError(
                f"{subject_label_col}/{session_label_col} is not unique in csv"
            )
    elif not csv_df[subject_label_col].is_unique:
        raise ValueError(f"{subject_label_col} is not unique in csv")

    new_subject_col = Dotty(deid_template).get(new_subject_label_loc, "").strip("{} ")
    if new_subject_col in csv_df:
        if not csv_df[new_subject_col].is_unique:
            raise ValueError(f"{new_subject_col} is not unique in csv")

    return csv_df


def create_jinja_var_df(
    template_path: os.PathLike,
    origin: flywheel.Project | flywheel.Subject | flywheel.Session,
    csv_path: t.Optional[os.PathLike],
    session_level_profile: bool,
) -> t.Optional[pd.DataFrame]:
    """Creates a DataFrame of subject-specific deid template variables

    Args:
        template_path: Path to deid template
        origin: Flywheel container (Project, Subject, Session)
        csv_path: Path to mapping_csv
        session_level_profile: Whether df will be supporting session level profiles

    Returns:
        pd.DataFrame: Dataframe of subject-specific template updates, else None
    """
    meta_df, csv_df = None, None
    subj_vars, sess_vars, csv_vars = get_jinja_variables(template_path)
    if sess_vars and not session_level_profile:
        log.warning(
            "The deid_profile includes Jinja variable notation that specifies "
            "session-level metadata but the config option `session_level_profile` "
            "is set to False. These variables will be ignored, which may create "
            "an invalid deid profile. "
            f"Found variables: {', '.join(sess_vars)}."
        )
    if subj_vars or sess_vars:
        meta_df = get_meta_df(
            origin, subj_vars, sess_vars, session_level_profile=session_level_profile
        )
    if csv_vars and csv_path:
        csv_df = get_csv_df(
            template_path,
            csv_path,
            csv_vars=csv_vars,
            session_level_profile=session_level_profile,
        )
    elif csv_vars and not csv_path:
        # deid profile has CSV Jinja variables but no CSV was provided
        log.warning(
            "The deid_profile includes Jinja variable notation but no mapping_csv "
            "was provided to fill these variables. "
            f"Found variables: {', '.join(csv_vars)}."
        )
        # Just warn, or warn and exit?
    merge_on = ["subject.label"]
    if session_level_profile:
        merge_on.append("session.label")
    if isinstance(meta_df, pd.DataFrame) and isinstance(csv_df, pd.DataFrame):
        return pd.merge(meta_df, csv_df, on=merge_on, how="inner")
    elif isinstance(meta_df, pd.DataFrame):
        return meta_df
    return csv_df
