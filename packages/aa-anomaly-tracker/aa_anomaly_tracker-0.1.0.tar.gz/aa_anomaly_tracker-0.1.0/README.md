# AA Anomaly Tracker<a name="aa-anomaly-tracker"></a>
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](http://black.readthedocs.io/en/latest/)
Track and manage mining and ice anomalies in your corp or alliance via Alliance Auth.

---

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=2 -->

- [Installation](#installation)
  - [Step 1: Install the Package](#step-1-install-the-package)
  - [Step 2: Configure Alliance Auth](#step-2-configure-alliance-auth)
  - [Step 3: Finalizing the Installation](#step-3-finalizing-the-installation)
  - [Step 4: Setup Permissions](#step-4-setup-permissions)
- [Features](#features)
- [Screenshots](#screenshots)
- [Development](#development)

<!-- mdformat-toc end -->

---

## Installation<a name="installation"></a>

> [!NOTE]
>
> **AA Anomaly Tracker** requires at least **Alliance Auth v4.0.0** and `eveuniverse` for solar system data.
>
> Ensure your AA is up-to-date before installation.

---

### Step 1: Install the Package<a name="step-1-install-the-package"></a>

Make sure you are in your virtual environment, then install via pip:

```shell
pip install aa-anomalytracker
```

---

### Step 2: Configure Alliance Auth<a name="step-2-configure-alliance-auth"></a>

Add the following to the `INSTALLED_APPS` of your `local.py`

Configure your AA settings (`local.py`) as follows:

- Add `"anomalytracker",` to `INSTALLED_APPS`

Make sure that `eveuniverse` is also installed.

---

### Step 3: Finalizing the Installation<a name="step-4-finalizing-the-installation"></a>

Run static files collection and migrations

```shell
python manage.py collectstatic
python manage.py migrate
```

---

### Step 4: Setup Permissions<a name="step-4-setup-permissions"></a>

Now it's time to set up access permissions for your new greenlight module.

| ID                   | Description                       | Notes                                                                                                       |
| :------------------- | :-------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `basic_access` | Can access anomaly tracker	 | Base permission to view the tracker |
| `manage_anoms`      | Can add/edit/remove anomalies	      |  For managers                                      |

