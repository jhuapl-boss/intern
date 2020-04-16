# Change Log

---

## v0.10.0 — April 16, 2020

v0.10.0 is the _last_ version of `intern` that support Python 2.x. If you need Python 2 support, you must run `pip install intern==0.10.0`. The development team does not anticipate further development for Python 2, and support for Python 2 environments will be discontinued. In future versions of `intern`, it will be assumed that the user is on Python 3 (3.6 or above).

-   Allow the "~" character in config-file path pointers when creating a new `BossRemote`
-   `BossRemote#get_channel` now supports a single string argument of the form `bossdb://[collection]/[experiment]/[channel]`. Likewise, you can pass this string directly to, e.g., `BossRemote#get_cutout` as the first argument.
-   Chunked downloads and uploads enable arbitrarily large cutouts from `BossRemote`.

## v0.9.12

intern incorporates the access_mode parameter when grabbing cutouts of small AND large sizes.
Backwards compatibility with previous versions that make use of the no_cache boolean parameter.
Whenever a user makes use of the no_cache param intern will return a deprecation warning. The translation occurs in intern/remote/boss/remote.py and should be removed in future major version upgrades.
intern now uses an enum class to limit the possibility of cache modes.

-   access_mode = CacheMode.cache - Utilizes the cache and checks for dirty keys
-   access_mode = CacheMode.no_cache - Does not check the cache but does check for dirty keys
-   access_mode = CacheMode.raw - Does not check the cache and DOES NOT check for dirty keys

This is for functions:

-   intern.remote.boss.remote.py: `BossRemote.get_cutout()`
-   intern.serivce.boss.baseversion.py: `BaseVersion.get_cutout_request()`

## v0.9.11

Convenience functions added:

-   `BossRemote#get_experiment()`
-   `BossRemote#get_coordinate_frame()`
-   `BossRemote#get_neuroglancer_link()` get a neuroglancer URL from cutout arguments
-   `create_cutout` will now chunk large cutouts into smaller components to eliminate HTTP size limitation and timeout errors.

## v0.9.10

-   Intern now forwards no_cache option when breaking apart large cutouts.

## v0.9.9

-   Modified the intern `get_cutout()` `no_cache` option to default to true instead of false

## v0.9.8

-   BugFix: Removed extra slash after no-cache option on URL that was causing issues.

## v0.9.7

-   Added new no-cache option to the `get_cutout(... no_cache=True)` This option will pull directly from the S3. It should be used when reading large amounts of data at once. Using this option can also increase throughput as the cache can become a bottleneck if a large amount of data is cycled through the cache

## v0.9.6

-   Merged PR #14 from ben_dev - correctly populate downsample_status of ChannelResource.
-   Relaxed requests dependency to >= 2.11.1.

## v0.9.5

-   Added BossRemote.get_channel() to ensure users use a fully specified channel with the cutout service.
-   Allow experiment time units to be unspecified.

## v0.9.4

-   API v1
-   Fix recursion loop when breaking cutout into chunks.
-   Fix x-y mistake in chunking.
-   Coordinate frame hierarchy methods now `anisotropic` and `isotropic`.
-   Channels now have downsample_status.

## Sprint 7

**Rebranded as intern.**

## General changes:

-   Made Python 2 compatible.
-   Version no longer controlled by resources. Now passed into BossRemote constructor.
-   Imports simplified.
-   Older Boss API support removed.
-   Config dictionary can be used instead of a config file.
-   Cutout range args now passed as a list of ints instead of a string.
-   Separate list methods for each resource type provided for convenience.
-   JHU ndio dependencies removed from requirements.txt.
-   Additional legacy code removed
-   Can provide config for each service or globally under the [Default] section of the config file
-   Can provide config via environment variables
-   Changed from a noun_verb convention to a verb_noun convention for function names

## v0.7 changes:

-   User management now done through entirely through SSO (Keycloak) server.
-   Resource, group, and permission API updates reflected in intern

## Sprint 4

---

### v0.5 changes:

-   New `ndio.remote.boss.remote.Remote` methods that support user and access management:
-   `group_create()`
-   `group_delete()`
-   `group_get()`
-   `group_add_user()`
-   `permissions_add()`
-   `permissions_get()`
-   `permissions_delete()`
-   `user_get_roles()`
-   `user_add_role()`
-   `user_delete_role()`
-   `user_get()`
-   `user_get_groups()`
-   `user_add()`
-   `user_delete()`
-   Only the name and description of a coordinate frame, can be changed, after creation.

### General changes:

-   `ndio.remote.boss.remote.Remote` method changes:
-   Exceptions are raised when any non-2xx response received from the Boss.
-   Methods that previously returned True to indicate success no longer return a value. Instead, an exception indicates failure (see above).
-   `project_create()` returns an `ndio.resource.boss.resource.Resource` instead of a dictionary.
-   `project_get()` returns an `ndio.resource.boss.resource.Resource` instead of a dictionary.
-   `project_update()` returns an `ndio.resource.boss.resource.Resource` instead of a bool.
-   `ndio.resource.boss.resource.ChannelResource` no longer allows the uint64 data type.

---

## Sprint 3

---

Initial release.

---
