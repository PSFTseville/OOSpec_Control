import json


if __name__ == "__main__":
    # Example usage of the code
    example_data = {
        'OceanHR1':{
            "integration_time": "numeric",
            "average": "numeric",
            "spectra": "signal",
            "calibration": 'numeric'
            },
        'OceanHR2':{
            "integration_time": "numeric",
            "average": "numeric",
            "spectra": "signal",
            "calibration": 'numeric'
            },
        'OceanHR3':{
            "integration_time": "numeric",
            "average": "numeric",
            "spectra": "signal",
            "calibration": 'numeric'
            },
    }
    
    with open('OHR_Spectro.json', 'w') as f:
        json.dump(example_data, f)
    
    print("Example data saved to 'example_data.json'.")
    
    # Load the example data
    with open('OHR_Spectro.json', 'r') as f:
        loaded_data = json.load(f)
    
    print("Loaded data:", loaded_data)