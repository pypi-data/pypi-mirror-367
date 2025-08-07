# python3-toolforge-weld

Shared Python code for Toolforge infrastructure components.

## Local development environment (guideline)

### Testing with tox on debian

Clone the repo (instructions here https://gitlab.wikimedia.org/repos/cloud/toolforge/toolforge-weld).

Install tox (this is the only debian-specific part):
```
~:$ apt install tox
```

Move to the directory where you cloned the repo, and run tox:
```
/path/to/repo/toolforge-weld:$ tox
```

That will run the tests and create a virtualenv that you can use to manually debug anything you need, to enter it:
```
/path/to/repo/toolforge-weld:$ source .tox/py3-tests/bin/activate
```

## Building the debian packages

The process will be:
* Create new branch
* Bump the version
* Build and deploy the package
* Upload the package to the toolforge repositories
* Merge PR and Create a release



Let's get started!

### Create new branch
To get started, create a new branch from main:
```
~:$ git checkout -b <new-branch-name>
```

### Bump the version
#### Update the changelog and setup.py
1. To do so, you can run the script:
    ```
    ~:$ utils/bump_version.sh
    ```

    That will:

    * create an entry in `debian/changelog` from the git log since the last tag
    * bump the version in `setup.py` too
    * create the required commit and tag.

2. Once this is done, you should push the new commit and tag for review:
    ```
    git push -u origin <new-branch-name>
    git push origin <new_version>
    ```
    You can find out the value of the newly created tag by looking at your terminal output or running `git tags --list`

#### Create a patch and get it reviewed

On gitlab you should create a patch based on the above PR, then Review the `changelog` and the `setup.py` changes to make sure it's what you want (it uses your name, email, etc.), and ask
for reviews.

### Build and deploy the package
#### Build and deploy with cookbook (Recommended)

> **NOTE**: Currently the PR created above needs to be open before you can use this cookbook. If you choose to use the more complicated alternatives below, keeping the PR open is not mandatory.

1. Building and deploying the package has been greatly simplified using the cookbook. To do this simply run:
    ```
    ~:$ cookbook wmcs.toolforge.component.deploy --cluster-name toolsbeta --component toolforge-weld --git-branch bump_version
    ```
    The above builds the package, uploads it to the toolsbeta package repository, and installs it on all the toolsbeta bastions. To do the same for tools use `--cluster-name tools`.

    See https://wikitech.wikimedia.org/wiki/Spicerack/Cookbooks for details on cookbooks.

#### Build and deploy with containers
> **NOTE**: This will not allow you to sign your package, so if you need that try using the manual process.

1. You can build the package with:
    ```
    path/to/repo/toolforge-weld:$ utils/build_deb.sh
    ```
    The first time it might take a bit more time as it will build the core image to build packages, downloading many
    dependencies. The next run it will not need to download all those dependencies, so it will be way faster.

    > **NOTE**: If it failed when installing packages, try passing `--no-cache` to force rebuilding the cached layers.

2. After building, you'll need to upload the built package to toolforge package repository. See [`Uploading to the toolforge repository`](#uploading-to-the-toolforge-repository) for more details.

3. Once you are done uploading, you also need to login to the various bastions on both tools and toolsbeta to manually install the package there.
    For example to install on toolsbeta bastion 6:
    ```
    ~:$ ssh toolsbeta-bastion-6.toolsbeta.eqiad1.wikimedia.cloud
    ~:$ sudo apt-get update && sudo apt-get install python3-toolforge-weld
    ```
    It is important to check how many bastions we have for both tools and toolsbeta and do this for all. You can ask the toolforge team if you don't have this information.




#### Build and deploy with wmcs-package-build script
1. Another alternative is using the wmcs-package-build.py script that you can find in
the operations/puppet repo at modules/toolforge/files

    ```
    $ ./wmcs-package-build.py --git-repo https://gitlab.wikimedia.org/repos/cloud/toolforge/toolforge-weld -a buster-toolsbeta -a bullseye-toolsbeta --git-branch main --build-dist=bullseye --backports --toolforge-repo=tools
    ```

    The script will SSH into a build server, build the package there, and publish it
    to two repos: `buster-toolsbeta` and `bullseye-tooslbeta`.

    The additional params `--backports, --toolforge-repo=tools
    --build-dist=bullseye` are necessary because the build requires Poetry and other
    build tools not available in the buster repos.

2. If that command is successful, you should then copy the package from the
"toolsbeta" to the "tools" distribution. See [`Uploading to the toolforge repository`](#uploading-to-the-toolforge-repository) for more details.

3. Once you are done uploading, you also need to login to the various bastions on both tools and toolsbeta to manually install the package there.
    For example to install on toolsbeta bastion 6:
    ```
    ~:$ ssh toolsbeta-bastion-6.toolsbeta.eqiad1.wikimedia.cloud
    ~:$ sudo apt-get update && sudo apt-get install python3-toolforge-weld
    ```
    It is important to check how many bastions we have for both tools and toolsbeta and do this for all. You can ask the toolforge team if you don't have this information.

Additional documentation on the wmcs-package-build script is available at
https://wikitech.wikimedia.org/wiki/Portal:Toolforge/Admin/Packaging#wmcs-package-build


### Uploading to the toolforge repository

If you built the package using any of the manual methods, you can uploade it following:
https://wikitech.wikimedia.org/wiki/Portal:Toolforge/Admin/Packaging#Uploading_a_package

### Merge PR and Create a release
Depending on the deployment method you chose, the PR might still be open. If that's the case remember to merge the PR and create a new Gitlab release.
