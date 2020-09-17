# How to write modules

First of all, please have a look at the [Ansible module development](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html) guide and get familiar with the general Ansible module layout.

When looking at actual modules in this repository ([`domain`](../plugins/modules/domain.py) is a nice short example), you will notice a few differences to a "regular" Ansible module:

* Instead of `AnsibleModule`, we use `ForemanEntityAnsibleModule` (and a few others, see [`plugins/module_utils/foreman_helper.py`](../plugins/module_utils/foreman_helper.py)) which provides an abstraction layer for talking with the Foreman API
* Instead of Ansible's `argument_spec`, we provide an enhanced version called `foreman_spec`. It handles the translation from Ansible module arguments to Foreman API parameters, as nobody wants to write `organization_ids` in their playbook when they can write `organizations`
* In addition to Ansible's validation options, we provide `required_plugins` which will check for installed Foreman plugins should the module require any.

The rest of the module is usually very minimalistic:
* Create a Sub class of `ForemanEntityAnsibleModule` for your module called `ForemanMyEntityModule` to work with `MyEntity` foreman resource and use this one for your module definition.
  Eg: If the foreman entity is named `Architecture`:
  ```python
  [...]

  class ForemanArchitectureModule(ForemanEntityAnsibleModule):
      pass


  [...]
  ```
* Connect to the API and run the module
  Eg: Like previous example, if the foreman entity is named `Architecture`:
  ```python
  [...]

  def main():
      module = ForemanArchitectureModule(
          argument_spec=dict(
              [...]
          ),
          foreman_spec=dict(
              [...]
          ),
      )

      with module.api_connection():
          module.run()


      if __name__ == '__main__':
          main()
  ```
You can see a complete example of simple module in [`architecture`](../plugins/modules/architecture.py)
In some cases, you will have to handle some custom workflows/validations, you can see some examples in [`bookmark`](../plugins/modules/bookmark.py), [`compute_attribute`](../plugins/modules/compute_attribute.py), [`hostgroup`](../plugins/modules/hostgroup.py), [`provisioning_template`](../plugins/modules/provisioning_template.py)...

## Specification of the `foreman_spec`

The `foreman_spec` can be seen as an extended version of Ansible's `argument_spec`. It understands more parameters (e.g. `flat_name`) and supports more `type`s than the original version. An `argument_spec` will be generated from an `foreman_spec`. Any parameters not directly known or consumed by `foreman_spec` will be passed directly to the `argument_spec`.

In addition to Ansible's `argument_spec`, `foreman_spec` understands the following types:

* `type='entity'` The referenced value is another Foreman entity.
This is usually combined with `flat_name=<entity>_id`. If no flat_name is provided, fallback to `<entity>_id` where entity is the foreman_spec key. eg `default_organization=dict(type='entity')` => `flat_name=default_organization_id`.
* `type='entity_list'` The referenced value is a list of Foreman entities.
This is usually combined with `flat_name=<entity>_ids`. If no flat_name is provided, fallback to `singularize(<entity>)_ids` where entity is the foreman_spec key. eg `organizations=dict(type='entity_list')` => `flat_name=organization_ids`.
* `type='nested_list'` The referenced value is a list of Foreman entities that are not included in the main API call.
The module must handle the entities separately.
See domain parameters in [`domain`](../plugins/modules/domain.py) for an example.
The sub entities must be described by `foreman_spec=<sub_entity>_spec`.
* `invisible=True` The parameter is available to the API call, but it will be excluded from Ansible's `argument_spec`.
* `search_by='login'`: Used with `type='entity'` or `type='entity_list'`. Field used to search the sub entity. Defaults to value provided by `ENTITY_KEYS` or 'name' if no value found.
* `search_operator='~'`: Used with `type='entity'` or `type='entity_list'`. Operator used to search the sub entity. Defaults to '='. For fuzzy search use '~'.
* `resource_type='organizations'`: Used with `type='entity'` or `type='entity_list'`. Resource type used to build API resource PATH. Defaults to pluralized entity key.
* `resolve=False`: Defaults to 'True'. If set to false, the sub entity will not be resolved automatically.
* `ensure=False`: Defaults to 'True'. If set to false, it will be removed before sending data to the foreman server.
* `scope=['organization']`: Defaults to '[]'. A list of entities that are used to build the lookup scope for this one.

`flat_name` provides a way to translate the name of a module argument as known to Ansible to the name understood by the Foreman API.

You can add new or override generated Ansible module arguments, by specifying them in the `argument_spec` as usual.

## Entity lookup

Sometimes you need to access entities before `module.run()` can take over.
You can trigger the automatic lookup of entities via `<entity_variable> = module.lookup_entity('<entity_name>')`.
If you only need the entity to be used as a scope parameter, it is enough to call `scope = module.scope_for('organization')`.

In case, the automatic lookup process is unable perform the proper find for a specific entity type, it must be looked up manually and then set via `module.set_entity('<entity_name>', search_result)` to prevent the automatism from trying.

In instances of `ForemanEntityAnsibleModule` the main entity is references as 'entity' in the above context.

## required_plugins

A module can pass an optional `required_plugins` list to `ForemanAnsibleModule`, which will indicate whether the module needs any Foreman plugins to be installed to work.

You can either specify that the whole module needs a specific plugin, like Katello modules:

```python
required_plugins=[
    ('katello', ['*']),
]
```

Or specific parameters, like the `discovery_proxy` parameter of `subnet` which needs the Discovery plugin:
```python
required_plugins=[
    ('discovery', ['discovery_proxy']),
]
```
