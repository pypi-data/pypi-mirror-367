"""Dataset environment constants for Fiddler AI platform.

This module defines environment types used when publishing inference data to Fiddler.
Environment types distinguish between pre-production baseline datasets and production
time-series monitoring data, enabling proper data classification and monitoring workflows.

Key Concepts:
    - **Pre-production Environment**: Static datasets used as baselines for comparison,
      typically training or validation data that represents expected model behavior
    - **Production Environment**: Time-series inference data from live model deployments
      that gets monitored against baselines for drift detection and performance tracking

Usage Pattern:
    Environment types are specified when publishing data to determine how Fiddler
    processes and monitors the data:

    ```python
    import fiddler as fdl

    # Publish baseline data (pre-production)
    model.publish(
        source=training_data,
        environment=fdl.EnvType.PRE_PRODUCTION,
        dataset_name='training_baseline'
    )

    # Publish live inference data (production)
    model.publish(
        source=inference_data,
        environment=fdl.EnvType.PRODUCTION
    )
    ```

See Also:
    - :class:`~fiddler.entities.Model` for data publishing methods
    - :class:`~fiddler.entities.Baseline` for baseline creation and management
    - Fiddler documentation on publishing inference data
"""

import enum


@enum.unique
class EnvType(str, enum.Enum):
    """Environment types for data publishing in Fiddler.

    This enum defines the two primary environment types used when publishing
    inference data to Fiddler. The environment type determines how Fiddler
    processes, stores, and monitors the data.

    Attributes:
        PRODUCTION: Live inference data from production model deployments
        PRE_PRODUCTION: Static baseline datasets for drift detection reference

    Examples:
        Publishing pre-production baseline data:

        ```python
        # Upload training data as baseline
        baseline_job = model.publish(
            source='training_data.csv',
            environment=fdl.EnvType.PRE_PRODUCTION,
            dataset_name='training_baseline'
        )
        ```

        Publishing production inference data:

        ```python
        # Stream live inference events
        model.publish(
            source=inference_events,
            environment=fdl.EnvType.PRODUCTION
        )
        ```

        Environment-specific data handling:

        ```python
        # Different processing based on environment
        if env_type == fdl.EnvType.PRE_PRODUCTION:
            # Static dataset - immutable after upload
            # Used for baseline calculations
            # No time-series monitoring
            pass
        elif env_type == fdl.EnvType.PRODUCTION:
            # Time-series data - continuous monitoring
            # Compared against baselines for drift
            # Subject to data retention policies
            pass
        ```

    Note:
        Environment types cannot be changed after data publication. Choose the
        appropriate environment based on your data's intended use case.
    """

    PRODUCTION = 'PRODUCTION'
    """Production environment for live inference data.

    Used for time-series inference data from live model deployments. This data:
    - Gets monitored continuously for drift and performance issues
    - Is compared against baseline datasets for anomaly detection
    - Supports real-time streaming and batch publishing
    - Is subject to data retention policies (typically 90 days)
    - Enables alert rule evaluation and dashboard visualization

    Typical use cases:
    - Live model inference results
    - Real-time prediction streaming
    - Batch inference job outputs
    - A/B testing data
    - Production model monitoring

    Data characteristics:
    - Time-series with timestamps
    - Continuous data flow
    - Variable data volumes
    - Monitored for drift patterns
    """

    PRE_PRODUCTION = 'PRE_PRODUCTION'
    """Pre-production environment for baseline datasets.

    Used for static datasets that serve as reference points for monitoring.
    This data:
    - Remains immutable after publication
    - Serves as baseline for drift detection calculations
    - Represents expected model behavior and data distributions
    - Is retained indefinitely for comparison purposes
    - Does not appear in time-series monitoring charts

    Typical use cases:
    - Training dataset baselines
    - Validation dataset references
    - Historical "golden" datasets
    - Model performance benchmarks
    - Data distribution references

    Data characteristics:
    - Static, unchanging datasets
    - Representative of expected distributions
    - Used for statistical comparisons
    - No time-series component
    """
