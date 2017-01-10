### INSTALLATION GUIDE

At this time sqlChain is only tested on Linux servers. It may work on other platforms but I don't have them to test and probably won't put effort into that in the near future. 

There is a new sqlchain-init script that handles most of the configuration and DB init details. 

Tested on a clean Ubuntu 14.04 Amazon EC2 instance (ami-feed08e8). I used a spot m4.large instance which costs only 1.4 cents/hour to test (plus data transfer out, which seems to be pretty substanial, and maybe the main cost).

### Getting Started - Step by Step

First, you need Bitcoin Core and some standard Ubuntu packages for MySQL and Python.

```
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install bitcoind mysql-server libmysqlclient-dev python-pip python-dev
```

Then you can install sqlChain from PyPi the easy way, includes dependencies and demo API web pages.

    sudo pip install sqlchain

That creates binaries in /usr/local/bin and puts python stuff where it should normally go.

The easy way to create the DB and configure and co-ordinate both bitcoin core and sqlchain daemons:

    sudo sqlchain-init
    
Answer the questions and it will create a user, mysql db and config files with correct permissions in locations you indicate. There are defaults for everything so you can get by with hitting 'Enter' the whole way thru. It also can be run again to change options but does not remove old files. It won't clobber the database either - you have to do that manually. It will create some demo api/web server files which you can build upon.

Finally, try starting the daemons, one at a time at first (this uses the upstart init process, which also starts them at boot).

```
sudo start bitcoin
sudo start sqlchain
sudo start sqlchain-api
```

If the process doesn't seem to start you can check in /var/log/upstart/ for logs upstart makes when something goes wrong. If a process starts but has other issues you can monitor them in their log files, by default directories as below,

```
/var/data/bitcoin/debug.log
/var/data/sqlchain/daemon.log
/var/data/sqlchain/api.log
```

You can add your normal user to the sqlchain/bitcoin group (by default "btc"),

    sudo adduser <myuser> btc
    
That allows you to use the config files easily, such as when using bitcoin-cli. It's also useful to have some aliases for common tasks. You can throw these in your .bashrc so they are present on login.

```
alias btc='bitcoin-cli -conf=/etc/bitcoin/bitcoin.conf'
alias sqdlog='sudo less /var/data/sqlchain/daemon.log'
```

### Updating

If you want to update sqlchain as I implement or fix stuff,

    sudo pip install --upgrade sqlchain
    
should do the trick. Bitcoin will get updated by the Ubuntu PPA package system (unless you do a custom build for manual pruning).

### Other Details

By default the API server (sqlchain-api) listens on localhost:8085 but of course a simple edit of sqlchain-api.cfg allows changing that. For example, to listen on the normal public port, assuming root privileges (when started as root it will drop to chosen user after):

    "listen":"0.0.0.0:80",
    
You can also set an SSL certificate file to use if you want to serve https. Again, edit the sqlchain-api.cfg and add:

    "ssl":"path/to/certfile",
    
This would be a file with concatenated private key and certificate blocks. It should have suitable secure permissions.

If you select "pruning" mode in the sqlchain-init questions then it will send rpc calls to bitcoin to let it know when a block is processed. Bitcoin prunes in "block file units", each one being ~128MB. So when sqlchaind has completed all blocks in a given block file it is deleted. The pruning only works in manual mode and this is currently non-standard. There is a nice pull request (#7871) in the bitcoin github to enable this but you would have to clone the repo, merge the pull request and build a custom binary. That's not hard to do and I can add a similar step-by-step if anyone requests it. It seems a custom build installs into /usr/local/bin instead of /usr/bin - so that overrides the normal bitcoind allowing you to use a full path to select which to start (change conf file to match).

Any questions or suggestions - post issues on GitHub or comments on my blog or send a message through my web site.

