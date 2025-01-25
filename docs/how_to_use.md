# How to Use

## Load Data

Having a file `people.csv` with the following content:

```csv
Jim Halpert, Sales, Salesman, jim@dundiermifflin.com
Dwight Schrute, Sales, Manager, schrute@dundiermifflin.com
Gabe Lewis, Director, Manager, glewis@dundiermifflin.com
```

Run `dundie load` command

```py
dundie load people.csv
```

## Viewing Data

### Viewing all information

```bash
                                          Dundler Mifflin Report                                           
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ E-Mail                     ┃ Dept    ┃ Role     ┃ Name           ┃ Balance ┃ Last_Movement              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ jim@dundiermifflin.com     │ Sales   │ Salesman │ Jim Halpert    │ 500     │ 2025-01-25T15:46:41.654546 │
│ schrute@dundiermifflin.com │ Sales   │ Manager  │ Dwight Schrute │ 100     │ 2025-01-25T15:46:41.654556 │
│ glewis@dundiermifflin.com  │ C-Level │ CEO      │ Gabe Lewis     │ 100     │ 2025-01-25T14:58:28.289354 │
└────────────────────────────┴─────────┴──────────┴────────────────┴─────────┴────────────────────────────┘
```

### Filtering

Available filters are `--dept` and `--email`

```bash
dundie show --dept=Sales
                                         Dundler Mifflin Report                                          
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ E-Mail                     ┃ Dept  ┃ Role     ┃ Name           ┃ Balance ┃ Last_Movement              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ jim@dundiermifflin.com     │ Sales │ Salesman │ Jim Halpert    │ 500     │ 2025-01-25T15:46:41.654546 │
│ schrute@dundiermifflin.com │ Sales │ Manager  │ Dwight Schrute │ 100     │ 2025-01-25T15:46:41.654556 │
└────────────────────────────┴───────┴──────────┴────────────────┴─────────┴────────────────────────────┘
```

> **NOTE**: Passing `--output=file.json` will save a json file with the results.

## Adding points

An admin user can easily add points to any user or department.

```bash
dundie add 100 --email=jim@dundiermifflin.com
                                      Dundler Mifflin Report                                      
┏━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ E-Mail                 ┃ Dept  ┃ Role     ┃ Name        ┃ Balance ┃ Last_Movement              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ jim@dundiermifflin.com │ Sales │ Salesman │ Jim Halpert │ 600     │ 2025-01-25T16:29:33.059578 │
└────────────────────────┴───────┴──────────┴─────────────┴─────────┴────────────────────────────┘
```

Available selectors are `--email` and `--dept`.