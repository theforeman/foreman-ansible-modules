# Releasing the collection

To release the collection the following steps are required:

* Create a pull request to update `galaxy.yml` with:
  * Version bump
  * Updated list of authors
    You can generate that list via `git shortlog -e -s | sed -E 's/^\s+[[:digit:]]+\s+(.*)$/ - "\1"/'`.

* After merging, tag the merge commit with `v<version number>` (i.e. v0.1.1).
  Please use signed tags.

Consider filing a packaging PR on [foreman-packaging](https://github.com/theforeman/foreman-packaging).
