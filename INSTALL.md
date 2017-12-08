### INSTALLATION GUIDE

At this time sqlChain is only tested on Linux servers. It may work on other platforms but I don't have them to test and probably won't put effort into that in the near future. 

There is a new **sqlchain-config** script that handles most of the configuration and DB init details. 

Tested on a clean Ubuntu 16.04 [Vultr.com](http://www.vultr.com/?ref=7087266) (1vCPU,2GB,40GB SSD) instance. If you try them then please use my [affiliate link](http://www.vultr.com/?ref=7087266) - gives me some much needed server credit for testing.

### Getting Started - Step by Step

First, you need Bitcoin Core and some standard Ubuntu packages for MySQL and Python.

```
sudo apt-get install software-properties-common python-software-properties libev-dev libevent-dev   # may not need but won't hurt
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt-get update
sudo apt-get install bitcoind mysql-server libmysqlclient-dev python-pip python-dev build-essential dialog
```

Then you can install sqlChain from PyPi the easy way, includes dependencies and demo API web pages.

    sudo pip install --upgrade pip  # may need this, won't hurt
    sudo pip install setuptools     # likewise
    
    sudo pip install sqlchain

That creates binaries in /usr/local/bin and puts python stuff where it should normally go.

The easy way to create the DB and configure and co-ordinate both bitcoin core and sqlchain daemons:

    sudo sqlchain-config
    
This is a terminal dialog based tool that will create a user, mysql db and config files with correct permissions in locations you indicate. There are defaults for everything so you can get by with selecting (8) Update on the settings menu. It will create some demo api/web server files which you can build upon.

Finally, try starting the daemons, one at a time at first, and check they're running with `htop` or `ps afx`:

```
sudo systemctl start bitcoin
sudo systemctl start sqlchain@bitcoin
sudo systemctl start sqlchain-api@bitcoin
```

If the process doesn't seem to start you can check what happened with the usual systemctl status commands:

```
sudo systemctl status bitcoin
sudo systemctl status sqlchain@bitcoin
sudo systemctl status sqlchain-api@bitcoin
```

It's a good idea to add your normal user to the sqlchain/bitcoin group (by default "btc"),

    sudo adduser <myuser> btc
    
That allows you to use the config files easily, such as when using bitcoin-cli. It's also useful to have some aliases for common tasks. You can throw these in your .bash_aliases so they are present on login. Just the most basic ones to build on:

```
alias btc='bitcoin-cli -conf=/etc/sqlchain/bitcoin.conf'
alias sqdlog='sudo less /var/data/sqlchain/bitcoin/daemon.log'
```

### Updating

If you want to update sqlchain as I implement or fix stuff,

    sudo pip install --upgrade sqlchain
    
should do the trick. Bitcoin will get updated by the Ubuntu PPA package system (unless you do a custom build for manual pruning). 

You can also install git and create a "bare init" repo. There are post-receive and deploy scripts in the docs directory as an example of automating updates. This allows simply "pushing" any updates to the repo and they get installed to correct locations.

### Pruning Mode

If you select "pruning" mode in the sqlchain-config options then it will send rpc calls to bitcoin to let it know when a block is processed. Bitcoin prunes in "block file units", each one being ~128MB. So when sqlchaind has completed all blocks in a given block file it is deleted. The pruning only works in manual mode and this is available in bitcoind >= 0.14.1 (otherwise you need to custom build bitcoind).

### Testnet / Other blockchains (as of version 0.2.5)

sqlChain and the sqlchain-config script now support multiple blockchains. Currently bitcoin, testnet, litecoin and reddcoin have config settings and have been tested. I expect to add more coins as I get time to install and test.

### Alternate Database Engines

I've tested RocksDB and TokuDB using MariaDB 10.2. Both worked well and saved around 50% space compared to MyISAM, and probably a lot more compared to InnoDB (which I have not yet tested). RocksDB syncs faster than others and is probably my recommended best choice for now, though it admitedly needs more testing. You can now set the engine type in the sqlchain-config DB options.

### Other Details

You should probably create an optimized my.cnf override file in /etc/mysql/conf.d/bitcoin.cnf which has values suited to your system. For example I use below with 8 GB RAM and it seems to improve speed (but don't claim this is optimal). The latest versions of MySQL seem to also add a mysql.conf.d directory and order of configuration is non-deterministic so you may need to play with the cnf location and name while checking how variables get set. This bizarre and confusing cnf loading wasn't a problem for me in earlier versions; call it progress.

    #optimized for bitcoin database using values from mysqltuner.pl adjusted for other uses
    [mysqld]
    ignore-builtin-innodb
    default-storage-engine = myisam
    key_buffer_size=6000M
    query_cache_type=0
    
    tmp_table_size=32M
    max_heap_table_size=32M

By default the API server (sqlchain-api) listens on localhost:8085 but of course a simple edit of sqlchain-api.cfg allows changing that. For example, to listen on the normal public port, assuming root privileges (when started as root it will drop to chosen user after):

    "listen":"0.0.0.0:80",
    
You can also set an SSL certificate file to use if you want to serve https. I would suggest for public access it's better to use nginx as a reverse proxy. It's fairly easy to setup and better for several reasons, one being secure certificate handling. But, you can edit the sqlchain-api.cfg and add:

    "ssl":"path/to/full-chain-certificate-file",
    "key":"path/to/private-key-file",     (optional: don't set if you use a combined key+cert in above)
    
This could be a file with concatenated private key and certificate blocks, or separate files. It should have read-only permissions; due to how python handles ssl it needs to be readable by the running user.

A simple proxy config for nginx is below. You could have several api servers behind nginx and it can load balance across them. 

    server {
        listen 80;
        listen [::]:80;
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name example.com www.example.com;
    
        ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    
        location / {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass http://127.0.0.1:8085;
        }
    }

It is also probably better for serving static content and only passing api calls to sqlchain-api, in which case use a blank www in sqlchain-api.cfg to disable root files. eg.

    "www":"",

The sqlchain-api "dbinfo" cfg option sets whether db state queries are run and at what interval: -1 = never, 0 = at start only, >0 minute interval. The db info output is available as an API call. So the following will refresh info every 10 minutes.

    "dbinfo":10,

Any questions or suggestions - post issues on GitHub.



