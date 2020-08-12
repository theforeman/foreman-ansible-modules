# Releasing the collection

To release the collection the following steps are required:

* Create a pull request with the following changes:
  * Updated `galaxy.yml`:
    * Version bump
    * Updated list of authors.

      You can generate that list via `git shortlog -e -s | sed -E 's/^\s+[[:digit:]]+\s+(.*)$/  - "\1"/'`.
  * Updated changelog by running `antsibull-changelog release` -- it will pick up the version from `galaxy.yml`

* After merging, tag the merge commit with `v<version number>` (i.e. v0.1.1).
  Please use signed tags.

Consider filing a packaging PR on [foreman-packaging](https://github.com/theforeman/foreman-packaging).
