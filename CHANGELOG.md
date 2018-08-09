# Change Log
____________
## v0.9.7
* Added new no-cache option to the get_cutout(... no_cache=True)  This option will pull directly from the S3.  It should be used when reading large amounts of data at once.  Using this option can also increase throughput as the cache can become a bottleneck if a large amount of data is cycled through the cache.

## v0.9.6
* Merged PR #14 from ben_dev - correctly populate downsample_status of ChannelResource.
* Relaxed requests dependency to >= 2.11.1.

## v0.9.5
* Added BossRemote.get_channel() to ensure users use a fully specified channel with the cutout service.
* Allow experiment time units to be unspecified.

## v0.9.4
* API v1
* Fix recursion loop when breaking cutout into chunks.
* Fix x-y mistake in chunking.
* Coordinate frame hierarchy methods now `anisotropic` and `isotropic`.
* Channels now have downsample_status.

## Sprint 7

**Rebranded as intern.**

## General changes:
* Made Python 2 compatible.
* Version no longer controlled by resources.  Now passed into BossRemote constructor.
* Imports simplified.
* Older Boss API support removed.
* Config dictionary can be used instead of a config file.
* Cutout range args now passed as a list of ints instead of a string.
* Separate list methods for each resource type provided for convenience.
* JHU ndio dependencies removed from requirements.txt.
* Additional legacy code removed
* Can provide config for each service or globally under the [Default] section of the config file
* Can provide config via environment variables
* Changed from a noun\_verb convention to a verb\_noun convention for function names

## v0.7 changes:
* User management now done through entirely through SSO (Keycloak) server.
* Resource, group, and permission API updates reflected in intern

## Sprint 4
___________

### v0.5 changes:
* New `ndio.remote.boss.remote.Remote` methods that support user and access management:
 * `group_create()`
 * `group_delete()`
 * `group_get()`
 * `group_add_user()`
 * `permissions_add()`
 * `permissions_get()`
 * `permissions_delete()`
 * `user_get_roles()`
 * `user_add_role()`
 * `user_delete_role()`
 * `user_get()`
 * `user_get_groups()`
 * `user_add()`
 * `user_delete()`
* Only the name and description of a coordinate frame, can be changed, after creation.

### General changes:
* `ndio.remote.boss.remote.Remote` method changes:
 * Exceptions are raised when any non-2xx response received from the Boss.
 * Methods that previously returned True to indicate success no longer return a value.  Instead, an exception indicates failure (see above).
 * `project_create()` returns an `ndio.resource.boss.resource.Resource` instead of a dictionary.
 * `project_get()` returns an `ndio.resource.boss.resource.Resource` instead of a dictionary.
 * `project_update()` returns an `ndio.resource.boss.resource.Resource` instead of a bool.
* `ndio.resource.boss.resource.ChannelResource` no longer allows the uint64 data type.

___________

## Sprint 3
___________

Initial release.

___________
