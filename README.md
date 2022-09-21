<!-- ABOUT THE PROJECT -->

## About The Project

A simple attendance project created with flask, react & mysql.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![React][react.js]][react-url]
- [![Mysql][mysql.dev]][mysql-url]
- [![Flask][flask.dev]][flask-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Prerequisites

- Docker

### Installation

1. Make sure to set env vars in a compose.env file within the docker-compose.dev.yml file directory

```sh
MYSQL_DB=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_HOST=
REMOTE_USERNAME=
REMOTE_PASSWORD=

MYSQL_ROOT_PASSWORD=
MYSQL_DATABASE=
MYSQL_USER=
MYSQL_PASSWORD=
```

2. Run the following command (need docker installed)
   ```sh
   docker-compose -f docker-compose.dev.yml up
   ```
3. Go to localhost:3050

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[mysql.dev]: https://img.shields.io/badge/Mysql-DD0031?style=for-the-badge&logo=mysql&logoColor=white
[mysql-url]: https://www.mysql.com/
[react.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[react-url]: https://reactjs.org/
[flask.dev]: https://img.shields.io/badge/Flask-563D7C?style=for-the-badge&logo=flask&logoColor=white
[flask-url]: https://flask.palletsprojects.com/en/2.2.x/
