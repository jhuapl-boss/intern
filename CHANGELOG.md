# Change Log
____________

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
 * `project_create()` returns an `ndio.ndresource.boss.resource.Resource` instead of a dictionary.
 * `project_get()` returns an `ndio.ndresource.boss.resource.Resource` instead of a bool.
 * `project_update()` returns an `ndio.ndresource.boss.resource.Resource` instead of a bool.
* `ndio.ndresource.boss.resource.ChannelResource` no longer allows the uint64 data type.

___________

## Sprint 3
___________

Initial release.

___________
