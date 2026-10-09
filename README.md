# Supply Chain Network Cost & Inventory Optimization

A reproducible Python project that optimizes shipments from **20 warehouses to 10 demand zones**, tests **10 demand/capacity scenarios**, and prepares CSV tables for a Power BI dashboard. It also estimates safety stock, reorder points, and replenishment priorities from synthetic daily-demand history.

> **Important:** This is a portfolio simulation built from synthetic data—not a real company's network or verified business result. The cost savings shown below are computed against the project's own greedy benchmark. Describe them as simulated results when using this repository.

## Results from the included synthetic scenario set

The model uses linear programming to minimize transportation cost subject to facility capacity, zone-level minimum service, and a network-wide fill-rate target.

| Metric | Reproducible result |
|---|---:|
| Warehouse nodes | 20 |
| Demand zones | 10 |
| Demand/capacity scenarios | 10 |
| Minimum network fill rate across scenarios | 96.0% |
| Base-scenario cost savings vs. greedy benchmark | 12.96% |
| Average cost savings across scenarios | 12.49% |
| Daily demand history | 600 synthetic observations (60 days × 10 zones) |

Run the model to recalculate these values. The numbers are not manually entered in the results table; they are calculated from the input CSVs and optimization outputs.

## Repository structure

```text
supply-chain-network-optimization/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── generate_data.py
│   ├── optimize_network.py
│   └── run_project.py
├── tests/
│   └── test_model.py
└── data/
    ├── input/
    │   ├── warehouses.csv
    │   ├── demand_zones.csv
    │   ├── shipping_costs.csv
    │   ├── scenario_inputs.csv
    │   ├── daily_demand_history.csv
    │   └── current_inventory.csv
    └── output/
        ├── scenario_summary.csv
        ├── optimized_shipments.csv
        ├── baseline_shipments.csv
        ├── warehouse_utilization.csv
        ├── zone_service_levels.csv
        └── inventory_policy_recommendations.csv
```

## Run it locally

### 1. Install Python dependencies

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment:

**macOS/Linux**

```bash
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

Then install the packages:

```bash
pip install -r requirements.txt
```

### 2. Run the complete project

From the repository root:

```bash
python src/run_project.py
```

This command recreates all synthetic input CSVs using a fixed random seed, solves the 10 scenarios, and writes the output CSVs to `data/output/`.

To regenerate input data only:

```bash
python src/generate_data.py
```

To rerun the optimization using the current input CSVs:

```bash
python src/optimize_network.py
```

### 3. Run validation tests

Run the project once, then run:

```bash
python -m unittest discover -s tests -v
```

The tests check the 96% network fill-rate target, minimum zone fill rates, warehouse capacities, cost improvement over the benchmark, and safety-stock output validity.

## How the optimization works

### Decision variable

Let \(x_{w,z}\) represent units shipped from warehouse \(w\) to demand zone \(z\).

### Objective

Minimize total transportation cost:

\[
\min \sum_w \sum_z c_{w,z} x_{w,z}
\]

where \(c_{w,z}\) is the synthetic per-unit lane cost.

### Constraints

- **Warehouse capacity:** outbound units from each warehouse cannot exceed its scenario-specific capacity.
- **Demand cap:** a zone cannot receive more units than its scenario demand.
- **Local service floor:** each zone receives at least 90% of its demand.
- **Network fill rate:** total shipped units must be at least 96% of total demand.
- **Non-negativity:** shipment quantities cannot be negative.

The linear program is solved with `scipy.optimize.linprog` using the HiGHS solver. Shipping is continuous, so quantities can be fractional in the model; output quantities are rounded for display, while calculations use unrounded solver values.

### Benchmark comparison

The baseline is a transparent heuristic: process demand zones from largest to smallest, and fulfill each zone by using the cheapest remaining-capacity warehouse lanes first until that zone reaches 96% fill. The LP optimizes all lanes jointly. `cost_savings_pct` is calculated as:

\[
100 \times \frac{\text{baseline cost} - \text{LP cost}}{\text{baseline cost}}
\]

This is a comparison against the project's heuristic—not a comparison against actual historical company spend.

## Scenario design

The scenario input contains paired demand and capacity multipliers. Examples include low demand, high demand, tight capacity, extra capacity, promotion surge, and mixed pressure. The input generation uses a fixed random seed so the portfolio output is reproducible. Coordinates are abstract map units and do not represent real addresses or cities.

The base network capacity is modeled at 98% of base-period demand, and the optimization enforces a 96% network fill rate. Scenario factors are selected so the modeled network remains feasible while still testing tighter and looser capacity conditions.

## Safety stock and replenishment policy

The project creates a synthetic 60-day demand history for each zone. It applies a 95% target service level and a normal-approximation safety-stock formula:

\[
\text{Safety Stock} = z \times \sigma_d \times \sqrt{L}
\]

where \(z=1.645\) for a one-sided 95% service target, \(\sigma_d\) is the standard deviation of daily demand, and \(L\) is replenishment lead time in days.

The reorder point is:

\[
\text{Reorder Point} = \bar d \times L + \text{Safety Stock}
\]

The output calculates inventory position as on-hand plus on-order units and flags a reorder gap. Priority bands are assigned as follows:

- **Critical:** inventory position is at or below safety stock.
- **High:** inventory position is at or below the reorder point.
- **Medium:** inventory position is no more than 1.25× the reorder point.
- **Low:** inventory position is above that threshold.

This is an educational policy illustration. It assumes independent daily demand and a fixed lead time per zone; a production solution would validate distributions, lead-time variability, order constraints, and business service-level targets.

## Output files

| File | What it contains | Suggested dashboard use |
|---|---|---|
| `scenario_summary.csv` | Demand, fill rates, baseline and optimized cost, savings by scenario | KPI cards and baseline-vs-optimized cost chart |
| `optimized_shipments.csv` | Positive LP shipment lanes and lane costs | Shipment flow, cost by warehouse/zone, route detail |
| `baseline_shipments.csv` | Shipment lanes under the greedy benchmark | Compare lane allocation against LP |
| `warehouse_utilization.csv` | Scenario capacity, outbound volume, and utilization | Warehouse utilization matrix or bar chart |
| `zone_service_levels.csv` | Demand, units filled, fill rate, and service floor by zone | Zone-level service heatmap |
| `inventory_policy_recommendations.csv` | Demand stats, lead time, safety stock, reorder point, inventory position, reorder gap, and priority | Replenishment priority table and action list |

## Build the Power BI dashboard

1. In Power BI Desktop, select **Get data → Text/CSV** and import the six CSVs from `data/output/`.
2. Use `scenario_id` to connect the scenario summary, shipments, and service/utilization tables. Use `zone_id` to connect zone service levels to inventory recommendations; use `warehouse_id` for warehouse-level drilldowns.
3. Create KPI cards for minimum optimized fill rate, base-scenario savings, average scenario savings, and count of High/Critical replenishment zones.
4. Add a clustered bar chart comparing `baseline_logistics_cost` and `optimized_logistics_cost` by `scenario_id`.
5. Add a matrix of `warehouse_id` by `scenario_id` using `utilization_rate`, and a zone table with `fill_rate` and `minimum_fill_rate`.
6. Add an inventory table with `zone_id`, `safety_stock_units`, `reorder_point_units`, `inventory_position_units`, `reorder_gap_units`, and `replenishment_priority`. Add scenario and priority slicers.

The repository exports dashboard-ready tables rather than a `.pbix` file, since Power BI report files are authored and saved in Power BI Desktop.

## Assumptions and limitations

- Every warehouse can serve every demand zone; no route, vehicle, labor, or product compatibility restrictions are modeled.
- Lane costs are synthetic and include distance-based cost plus a warehouse handling component.
- Shipment quantities are continuous; real operations may require integer cases, pallets, or truckloads.
- The service target is a constraint, not a forecast of achieved real-world performance.
- The inventory-policy calculation is separate from the shipping LP; it supports dashboard review but does not feed order quantities back into the network optimization.
- No real company, customer, supplier, or location data is included.

## Suggested resume wording

**Supply Chain Network Cost & Inventory Optimization**  
Modeled a 20-warehouse network using linear programming and scenario analysis; simulated a 12.96% base-case cost reduction versus a greedy benchmark while meeting a 96% fill-rate target. Built Power BI-ready outputs for warehouse utilization, zone service levels, safety stock, and replenishment priorities.

Keep the word **simulated** or otherwise clearly indicate that this is a synthetic portfolio case study. Replace these results only after you have a new reproducible model run supporting the new figures.
