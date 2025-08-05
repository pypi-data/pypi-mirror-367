import logging

from sqlalchemy import select
from xplan_tools.interface.db import DBRepository
from xplan_tools.model.orm import Feature

logger = logging.getLogger(__name__)


def get_db_feature_ids(
    repo: DBRepository,
    typenames: str | list | None = None,
    featuretype_regex: str | None = None,
    value_prop: str | None = None,
) -> dict:
    """
    Query the database for features matching the provided type(s) or regex, and
    return a mapping from feature IDs to label (from `value_prop`) or a fallback string.

    Args:
        repo (DBRepository): The database repository instance.
        typenames (str | list | None): Single typename or list of typenames to filter on.
        featuretype_regex (str | None): Optional regex to match featuretype.
        value_prop (str | None): The property to use for the label in the result dict.

    Returns:
        dict: Mapping from stringified feature ID to label or fallback.
    """
    logger.info("Entered db.get_db_feature_ids().")
    results = {}
    try:
        with repo.Session() as session:
            stmt = select(Feature)
            if typenames:
                names_list = [typenames] if isinstance(typenames, str) else typenames
                stmt = stmt.where(Feature.featuretype.in_(names_list))
                logger.info(f"Filtering for typenames: {names_list}")
            if featuretype_regex:
                stmt = stmt.where(Feature.featuretype.regexp_match(featuretype_regex))
                logger.info(f"Filtering with regex: {featuretype_regex}")
            try:
                db_result = session.execute(stmt)
                features = db_result.unique().scalars().all()
                logger.info(f"Found {len(features)} feature(s) in DB.")
            except Exception as db_ex:
                logger.error(f"Database query failed: {db_ex}", exc_info=True)
                return {}

            for feature in features:
                label = None
                try:
                    label = (
                        feature.properties.get(value_prop, None) if value_prop else None
                    )
                except Exception as prop_ex:
                    logger.warning(
                        f"Error accessing properties of feature ID {feature.id}: {prop_ex}",
                        exc_info=True,
                    )
                key = str(feature.id)
                value = label if label else f"{feature.featuretype}::{feature.id}"
                results[key] = value

    except Exception as ex:
        logger.error(f"Failed to get feature IDs: {ex}", exc_info=True)
        raise
    return results
