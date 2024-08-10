# Backup me

This tool is designed for backups. It allows backing up various databases and files to S3 compatible storages.

It is designed to be run as a Docker container.

> [!IMPORTANT]
> This tool is definitively **NOT production ready**, and will certainly never be. You shouldn't use it in a production critical environment. I know my way around databases and devops tools, but I don't claim to be a database backup expert.
>
> I have built this tool more as a hobby (yes I know, weird hobby...) and for a personal use cases. If you'd like to use, I'd be more than happy to help you.
>
> Please use more production ready and complete tools if you have real and serious use cases.

## Installation

Docker images are build for version and published on the GitHub container registry.

The available versions can be browsed in the [*Packages* of the repo](https://github.com/bastantoine/backup-me/pkgs/container/backup-me).

```shell
docker run ghcr.io/bastantoine/backup-me:latest
```

## Configuration

The tool can be configured with a `config.json` file, with the following structure:

```json
{
    "app": "<APP NAME>",
    "sources": [
        [...]
    ],
    "destinations": [
        [...]
    ]
}
```

- `app`: the name of the application currently being handled. This will be used in the name of the backups.
- `sources` is a list of one or more sources that needs to be backed up. The available sources are listed below.
- `destinations` is a list of one or more destination where to send the backups once they have been generated. The available destinations are listed below.

### Available sources

#### MySQL

```json
{
    "type": "mysql",
    "backup_filename": "mysql_backup",
    "host": "localhost",
    "port": "3306",
    "username": "username",
    "password": "password",
    "database": "--all-databases",
    "all_databases": true,
    "mysql_dump_bin": "/usr/local/opt/mysql-client/bin/mysqldump"
}
```

| Key               | Description                                           | Required | Default value                               |
| ----------------- | ----------------------------------------------------- | -------- | ------------------------------------------- |
| `type`            | Type of source                                        | Yes      | `"mysql"`                                     |
| `backup_filename` | Name of the backup file generated                     | Yes      |                                             |
| `host`            | Hostname of the MySQL server                          | Yes      |                                             |
| `port`            | Port to connect to the server                         | No       | 3306                                        |
| `username`        | Username to connect to the server                     | Yes      |                                             |
| `password`        | Password to connect to the server                     | Yes      |                                             |
| `database`        | Name of the database to backup                        | No*      |                                             |
| `all_databases`   | Whether to backup all databases of the server         | No*      | False                                       |
| `mysql_dump_bin`  | Path to the `mysql_dump_bin` tool used for the backup | No       | `"/usr/local/opt/mysql-client/bin/mysqldump"` |

> [!TIP]
> The `database` and `all_databases` parameters are mutually exclusive. One of them must be provided at all time. Config validation will fail if none are provided. If both are provided at the same time `all_databases` will have precedence.

#### PostgreSQL

```json
{
    "type": "postgres",
    "backup_filename": "pg_backup",
    "host": "0.0.0.0",
    "port": "5432",
    "username": "username",
    "password": "password",
    "database": "db",
    "all_databases": true,
    "pg_dump_bin": "/usr/local/opt/libpq/bin/pg_dump",
    "pg_dumpall_bin": "/usr/local/opt/libpq/bin/pg_dumpall"
}
```

| Key               | Description                                           | Required | Default value                           |
| ----------------- | ----------------------------------------------------- | -------- | --------------------------------------- |
| `type`            | Type of source                                        | Yes      | `"postgres"`                            |
| `backup_filename` | Name of the backup file generated                     | Yes      |                                         |
| `host`            | Hostname of the PostgreSQL server                     | Yes      |                                         |
| `port`            | Port to connect to the server                         | No       | 5432                                    |
| `username`        | Username to connect to the server                     | Yes      |                                         |
| `password`        | Password to connect to the server                     | Yes      |                                         |
| `database`        | Name of the database to backup                        | No*      |                                         |
| `all_databases`   | Whether to backup all databases of the server         | No*      | False                                   |
| `pg_dump_bin`     | Path to the `pg_dump_bin` tool used for the backup    | No       | `"/usr/local/opt/libpq/bin/pg_dump"`    |
| `pg_dumpall_bin`  | Path to the `pg_dumpall_bin` tool used for the backup | No       | `"/usr/local/opt/libpq/bin/pg_dumpall"` |

> [!TIP]
> The `database` and `all_databases` parameters are mutually exclusive. One of them must be provided at all time. Config validation will fail if none are provided. If both are provided at the same time `all_databases` will have precedence.

> [!TIP]
> The `pg_dump_bin` is used when backing up only one database (ie. when the `database` param is provided). When backing up the entire cluster, `pg_dumpall_bin` is used (ie. when the `all_databases` param is provided).

#### Raw files

```json
{
    "type": "files",
    "backup_filename": "config",
    "archive_type": "tar",
    "files": [
        "~/.vimrc",
        "~/.sqliterc",
        "~/.zshrc"
    ]
}
```

| Key               | Description                                      | Required | Default value |
| ----------------- | ------------------------------------------------ | -------- | ------------- |
| `type`            | Type of source                                   | Yes      | `"files"`     |
| `backup_filename` | Name of the backup file generated                | Yes      |               |
| `files`           | List of paths to files to back up in the archive | Yes      |               |
| `archive_type`    | Type of archive to create (`zip` or `tar`)       | No       | `"tar"`       |

> [!TIP]
> The paths in `files` can either be absolute, relative to the current user homedir, or relative the current working directory.

### Available destinations

#### S3

```json
{
    "type": "s3",
    "name": "<destination name>",
    "bucket": "my-bucket.for.backups",
    "group": true,
    "access_key_id": "XXXX",
    "secret_access_key": "XXXX",
    "prefix": null,
    "endpoint_url": "https://<s3 service>",
    "region": "us-east-1"
}
```

| Key                 | Description                                                                       | Required | Default value |
| ------------------- | --------------------------------------------------------------------------------- | -------- | ------------- |
| `type`              | Type of destination                                                               | Yes      | `"s3"`        |
| `name`              | Name of the destination                                                           | Yes      |               |
| `bucket`            | Name of the bucket to upload to                                                   | Yes      |               |
| `group`             | In case of multiple sources, whether to group all backups in a single tar archive | Yes      |               |
| `access_key_id`     | Access key to login to the S3 service                                             | Yes      |               |
| `secret_access_key` | Secret access key to login to the S3 service                                      | Yes      |               |
| `prefix`            | Prefix to the backup file                                                         | No       |               |
| `endpoint_url`      | Endpoint to the S3 service                                                        | No       |               |
| `region`            | Region of the S3 service                                                          | No       | `"us-east-1"` |


> [!TIP]
> The `access_key_id` and `secret_access_key` can be loaded from the environnement.
>
> The environment variables should be named respectively `S3_<name>_ACCESS_KEY_ID` and `S3_<name>_SECRET_ACCESS_KEY` with `<name>` being the name of the destination uppercased, and with spaces replaced by underscores.
>
> If a param is provided both in the config file and in the environement, the value of the config file will have precedence.