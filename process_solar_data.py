from pathlib import Path
from dateutil import parser
from datetime import datetime, timedelta
import json
import csv


def deaccumulate_solar(data):
    rows = []
    for key, issuance in data.items():
        previous = 0
        for leadtime_data in issuance:
            flux = float(leadtime_data["surface_net_downward_shortwave_flux"])
            leadtime_data["surface_net_downward_shortwave_flux"] = flux - previous
            rows.append(leadtime_data)
            previous = flux
        #     print(leadtime_data)
        # print()
    return rows


def get_json_data():
    data = {}
    paths = []
    # Get the complete list of JSON filenames
    for path in Path("sof-d").rglob("*.csv"):
        filepath = str(path)
        paths.append(filepath)

    paths = sorted(paths)

    for fpath in paths:
        with open(fpath) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                issuance = row["issuance_time"]
                vtime = row["valid_time"]
                flux = row["surface_net_downward_shortwave_flux"]
                d = {
                    "issuance": issuance,
                    "valid_time": vtime,
                    "surface_net_downward_shortwave_flux": flux,
                }
                if issuance in data:
                    data[issuance].append(d)
                else:
                    data[issuance] = [d]

    return deaccumulate_solar(data)


if __name__ == "__main__":

    data = get_json_data()

    # Set up the CSV writer
    fname = "combined_point_59.353400_18.063400.csv"
    with open(fname, "w") as csvfile:
        writer = csv.writer(csvfile)
        # Write the CSV header
        writer.writerow(
            (
                "Forecast Issuance",
                "Valid Time",
                "surface_net_downward_shortwave_flux",
            )
        )
        # Progress counter
        i = 1
        # Write CSV rows
        for x in data:
            issuance = x["issuance"]
            vtime = x["valid_time"]
            time_diff = parser.parse(vtime) - parser.parse(issuance)
            if time_diff <= timedelta(days=1):
                writer.writerow(
                    [
                        issuance,
                        vtime,
                        x["surface_net_downward_shortwave_flux"],
                    ]
                )
                print("Finishing writing row {}/{}".format(i, len(data)))
                i += 1
    print("Data saved to `{}`".format(fname))
