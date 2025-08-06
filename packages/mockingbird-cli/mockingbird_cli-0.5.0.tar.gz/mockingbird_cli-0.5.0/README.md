# Mockingbird 🐦

**Generate realistic mock data with relationships in seconds**

[![PyPI version](https://badge.fury.io/py/mockingbird-cli.svg)](https://badge.fury.io/py/mockingbird-cli)
[![Python Support](https://img.shields.io/pypi/pyversions/mockingbird-cli.svg)](https://pypi.org/project/mockingbird-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Mockingbird is a powerful CLI tool that generates realistic mock data with proper relationships and referential integrity. Perfect for testing, development, demos, and populating databases with meaningful data.

## ✨ Key Features

- **🎯 Realistic Data**: Generate names, emails, addresses, and more using the Faker library
- **🔗 Relational Integrity**: Create proper foreign key relationships between entities
- **📝 Simple Configuration**: Define your data structure in an intuitive YAML blueprint
- **🎲 Reproducible**: Use seeds to generate the same dataset consistently
- **📊 Multiple Formats**: Output to CSV, JSON, or Parquet
- **⚡ Fast Generation**: Efficiently create large datasets
- **🏗️ Complex Relationships**: Support for multi-level references and contextual data

## Project Home
[Project Home](https://mockingbird.smallapps.in/)

## 🚀 Quick Start

### Installation

```bash
pip install mockingbird
```

### Create Your First Dataset

1. **Initialize a blueprint:**
   ```bash
   mockingbird init
   ```

2. **Define your data structure** in `Blueprint.yaml`:
   ```yaml
   Users:
     count: 100
     fields:
       user_id: {generator: sequence, config: {start_at: 1}}
       name: {generator: faker, config: {generator: name}}
       email: {generator: faker, config: {generator: email}}
       status: {generator: choice, config: {choices: ["active", "inactive"], weights: [0.8, 0.2]}}

   Orders:
     count: 250
     fields:
       order_id: {generator: sequence, config: {start_at: 1000}}
       user_id: {generator: ref, config: {ref: Users.user_id}}
       order_date: {generator: faker, config: {generator: date_time_this_year}}
       amount: {generator: faker, config: {generator: pydecimal, left_digits: 3, right_digits: 2, positive: true}}
   ```

3. **Generate your data:**
   ```bash
   mockingbird generate  Blueprint.yaml
   ```

4. **Find your data** in the `output_data/` directory as CSV files!

## 🎯 Use Cases

- **🧪 Testing**: Create realistic test datasets for your applications
- **🔧 Development**: Populate development databases with meaningful data
- **📊 Demos**: Generate impressive demo data for presentations
- **⚡ Performance Testing**: Create large datasets to test system performance
- **🎓 Learning**: Practice with realistic data for tutorials and courses

## 🛠️ Generators

Mockingbird provides powerful generators for different data types:

| Generator | Purpose | Example |
|-----------|---------|---------|
| `sequence` | Auto-incrementing numbers | User IDs, Order numbers |
| `faker` | Realistic fake data | Names, emails, addresses |
| `choice` | Random selection from options | Status, categories, types |
| `ref` | Reference other entities | Foreign keys, relationships |
| `timestamp` | Random dates/times | Creation dates, events |
| `expr` | Custom expressions | Calculated fields, conditions |
| `enum` | Cycle through values | Round-robin assignments |

## 📖 Examples

### E-commerce Dataset

```yaml
Categories:
  count: 5
  fields:
    category_id: {generator: sequence, config: {start_at: 100}}
    name: {generator: choice, config: {choices: ["Electronics", "Books", "Clothing", "Home", "Sports"]}}

Products:
  count: 50
  fields:
    product_id: {generator: sequence, config: {start_at: 200}}
    name: {generator: faker, config: {generator: catch_phrase}}
    category_id: {generator: ref, config: {ref: Categories.category_id}}
    price: {generator: faker, config: {generator: pydecimal, left_digits: 3, right_digits: 2, positive: true}}

Customers:
  count: 25
  fields:
    customer_id: {generator: sequence, config: {start_at: 1000}}
    name: {generator: faker, config: {generator: name}}
    email: {generator: faker, config: {generator: email}}

Orders:
  count: 75
  fields:
    order_id: {generator: sequence, config: {start_at: 3000}}
    customer_id: {generator: ref, config: {ref: Customers.customer_id}}
    customer_name: {generator: ref, config: {use_record_from: customer_id, field_to_get: name}}
    order_date: {generator: faker, config: {generator: date_time_this_year}}

OrderItems:
  count: 200
  fields:
    item_id: {generator: sequence, config: {start_at: 4000}}
    order_id: {generator: ref, config: {ref: Orders.order_id}}
    product_id: {generator: ref, config: {ref: Products.product_id}}
    quantity: {generator: faker, config: {generator: random_int, min: 1, max: 4}}
    unit_price: {generator: ref, config: {use_record_from: product_id, field_to_get: price}}
```

### User Activity Tracking

```yaml
Users:
  count: 50
  fields:
    user_id: {generator: sequence}
    username: {generator: faker, config: {generator: user_name}}
    email: {generator: faker, config: {generator: email}}

Events:
  count: 500
  fields:
    event_id: {generator: sequence, config: {start_at: 10000}}
    user_id: {generator: ref, config: {ref: Users.user_id}}
    event_type: {generator: choice, config: {choices: ["login", "logout", "view_page", "purchase"]}}
    timestamp: {generator: timestamp, config: {start_date: "2024-01-01", end_date: "2024-12-31"}}
```

## 🎛️ Command Line Options

```bash
# Basic generation
mockingbird generate  Blueprint.yaml

# Custom blueprint and output
mockingbird generate Blueprint.yaml --output-dir ./data --format parquet

# Reproducible data with seed
mockingbird generate  Blueprint.yaml --seed 42

# Different output formats
mockingbird generate  Blueprint.yaml --format json
mockingbird generate  Blueprint.yaml --format parquet
```

## 📋 Requirements

- Python 3.11 or higher
- No additional dependencies required

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Documentation**: [Full User Manual](https://mockingbird.smallapps.in/)

## 🎉 Why Mockingbird?

Unlike other mock data generators, Mockingbird focuses on **relationships and realism**:

- ✅ **Smart References**: Automatic dependency resolution ensures data integrity
- ✅ **Contextual Data**: Pull related fields from the same record for consistency
- ✅ **Realistic Distributions**: Use weights to create realistic data patterns
- ✅ **Scalable**: Generate thousands of related records efficiently
- ✅ **Flexible Output**: Choose the format that works for your workflow

---

**Ready to generate some amazing mock data?** 🚀

```bash
pip install mockingbird-cli
mockingbird init
mockingbird generate Blueprint.yaml
```