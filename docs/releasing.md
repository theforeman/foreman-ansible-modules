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

* Bump the version once more to `<next version number>-dev` (i.e. 1.4.0-dev or 0.1.2-dev on a release branch).

Consider filing a packaging PR on [foreman-packaging](https://github.com/theforeman/foreman-packaging).

## Vendoring `apypie`

To make installations easier, we vendor a copy of `apypie` in our `module_utils`.

To update the copy, call `make vendor` and either pass `APYPIE_VERSION=vX.Y.Z` to the `make` invocation or update the `Makefile`.
