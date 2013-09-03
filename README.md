cuisine
=======

*Samples and recipes for Cuisine, a lightweight Chef/Puppet alternative in Python.*


### About Cuisine

[Cuisine](https://github.com/sebastien/cuisine) is a small set of functions that sit on top of Fabric, to abstract common administration operations such as file/dir operations, user/group creation, package install/upgrade, making it easier to write portable administration and deployment scripts.

## About our recipe

Currently, we have one recipe to automate a *Tomcat / MySQL / nginx* deployment on *Ubuntu 12.04 LTS server (64 bits)*.

It takes care of the numerous gory details of a server installation: configuration files at the right place with the right owner and privileges, database creation and database user creation, reverse-proxy configuration, basic maintenance scripts, authorized SSH keys for passwordless access, firewall (uwf) and more.

### How to install Cuisine

Follow the installation instructions [here](https://github.com/sebastien/cuisine). It is as simple as:

1. Creating a `venv` (optional)
2. `pip install cuisine`

### How to setup the recipe

1. Open `fab.py` and modify the configuration parameters on the top of the file.

2. Review the configuration files under `files` and adapt the settings according to your environment. There are no automatic substitutions yet based on the parameters you set on step 1.

3. It is advised (although not mandatory) to run the `virtualenv` utility in your project’s directory:

```python
$ virtualenv --distribute venv
```

To use the environment:

```python
$ source venv/bin/activate
```

Once you have finished working in the current virtual environment:

```python
$ source venv/bin/deactivate
```

### How to use

From the command line, run `fab` to launch the full setup. You may run an individual target, for instance `fab version` to check that your installation works.

Normally, you should be able to re-run the whole setup recipe even after you've already run it once.

### More about Cuisine

- An [introductory article](http://stackful-dev.com/cuisine-the-lightweight-chefpuppet-alternative) to get acquainted with Cuisine.
- A great [slide deck](http://stackful-dev.com/cuisine-the-lightweight-chefpuppet-alternative) if you want an in-depth introduction.
- Cuisine source to find out about the available functions.
- Our recipe in `fabfile.py`. Enhance it and adapt it to your needs.

### Target and sta

Should work on any host, be it in the cloud or in-house.

Tested on Amazon EC2 and on Linode. There is a switch dedicted to Amazon to bypass firewall (use security groups from the AWS console instead), ubuntu user (created for you with AMI) and ssh-key deployment (chosen by you in the instance creation wizard).

Ubuntu server images are updated every so often; therefore it is very possible that this script or the configuration files will fail to work at some point.

### Status

Running individual targets from a fresh installation has not been tested. Limited testing has been done, so play with it, tweak it and have fun! Pull requests welcome.