# Copyright 2024 Canonical Ltd.
# Licensed under the Apache V2, see LICENCE file for details.
"""Constants for facade version negotiation."""

from typing import Dict, Sequence

# Please keep in alphabetical order
# in future this will likely be generated automatically (perhaps at runtime)
client_facade_versions = {
    "Action": (7,),
    "Admin": (3,),
    "AllModelWatcher": (4,),
    "AllWatcher": (3,),
    "Annotations": (2,),
    "Application": (17, 19, 20),
    "ApplicationOffers": (4, 5),
    "Backups": (3,),
    "Block": (2,),
    "Bundle": (6,),
    "Charms": (6,),
    "Client": (6, 7, 8),
    "Cloud": (7,),
    "Controller": (11, 12),
    "CredentialManager": (1,),
    "FirewallRules": (1,),
    "HighAvailability": (2,),
    "ImageMetadataManager": (1,),
    "KeyManager": (1,),
    "MachineManager": (10,),
    "MetricsDebug": (2,),
    "ModelConfig": (3,),
    "ModelGeneration": (4,),
    "ModelManager": (9, 10),
    "ModelUpgrader": (1,),
    "Payloads": (1,),
    "Pinger": (1,),
    "Resources": (3,),
    "SSHClient": (4,),
    "SecretBackends": (1,),
    "Secrets": (1, 2),
    "Spaces": (6,),
    "Storage": (6,),
    "Subnets": (5,),
    "UserManager": (3,),
}

# Manual list of facades present in schemas + codegen which python-libjuju does not yet support
excluded_facade_versions: Dict[str, Sequence[int]] = {"Charms": (7,)}


# We don't generate code for these, as we can never use them.
# The controller happily lists them though, don't warn about these.
known_unsupported_facades = (
    "ActionPruner",
    "Agent",
    "AgentLifeFlag",
    "AgentTools",
    "ApplicationScaler",
    "CAASAdmission",
    "CAASAgent",
    "CAASApplication",
    "CAASApplicationProvisioner",
    "CAASFirewaller",
    "CAASFirewallerSidecar",
    "CAASModelConfigManager",
    "CAASModelOperator",
    "CAASOperator",
    "CAASOperatorProvisioner",
    "CAASOperatorUpgrader",
    "CAASUnitProvisioner",
    "CharmDownloader",
    "CharmRevisionUpdater",
    "Cleaner",
    "CredentialValidator",
    "CrossController",
    "CrossModelRelations",
    "CrossModelSecrets",
    "Deployer",
    "DiskManager",
    "EntityWatcher",
    "EnvironUpgrader",
    "ExternalControllerUpdater",
    "FanConfigurer",
    "FilesystemAttachmentsWatcher",
    "Firewaller",
    "HostKeyReporter",
    "ImageMetadata",
    "InstanceMutater",
    "InstancePoller",
    "KeyUpdater",
    "LeadershipService",
    "LifeFlag",
    "LogForwarding",
    "Logger",
    "MachineActions",
    "MachineUndertaker",
    "Machiner",
    "MeterStatus",
    "MetricsAdder",
    "MetricsManager",
    "MigrationFlag",
    "MigrationMaster",
    "MigrationMinion",
    "MigrationStatusWatcher",
    "MigrationTarget",
    "ModelSummaryWatcher",
    "NotifyWatcher",
    "OfferStatusWatcher",
    "PayloadsHookContext",
    "Provisioner",
    "ProxyUpdater",
    "Reboot",
    "RelationStatusWatcher",
    "RelationUnitsWatcher",
    "RemoteRelationWatcher",
    "RemoteRelations",
    "ResourcesHookContext",
    "RetryStrategy",
    "SecretBackendsManager",
    "SecretBackendsRotateWatcher",
    "SecretsDrain",
    "SecretsManager",
    "SecretsRevisionWatcher",
    "SecretsTriggerWatcher",
    "Singular",
    "StatusHistory",
    "StorageProvisioner",
    "StringsWatcher",
    "Undertaker",
    "UnitAssigner",
    "Uniter",
    "UpgradeSeries",
    "UpgradeSteps",
    "Upgrader",
    "UserSecretsDrain",
    "UserSecretsManager",
    "VolumeAttachmentPlansWatcher",
    "VolumeAttachmentsWatcher",
)
