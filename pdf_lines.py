# Let's recheck the PDF content for the correct line pattern and update extraction logic if needed.
from PyPDF2 import PdfReader
import re
import numpy as np


# constants
c = 299792458  # Speed of light in m/s

# Load the PDF again
reader = PdfReader("/home/jessalsua/OneDrive/SMART/GlowDischarge/ArLines.pdf")

# Define a better pattern to capture line tables more broadly
spectral_lines = []
active_ion = None
roman_numerals = {
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
    7: "VII",
    8: "VIII",
    9: "IX",
    10: "X",
    11: "XI",
    12: "XII",
    13: "XIII",
    14: "XIV",
    15: "XV",
    16: "XVI",
    17: "XVII",
    18: "XVIII"
}
ion_section_titles = {
    f"Spectral lines of Ar {roman_numerals[i]}": f"Ar {roman_numerals[i]}" for i in range(3, 19)
}

spectral_lines = {
    "Air": [],
    "Vacuum": [],
}


# Loop through all pages and extract matching lines
for i, page in enumerate(reader.pages):
    print(f"Processing page {i + 1} of {len(reader.pages)}")
    text = page.extract_text()
    if not text:
        continue

    lines = text.splitlines()
    current_line_type = None  # Reset for each page
    active_ion = None  # Reset for each page
    for j, line in enumerate(lines):
        # if i==149:
        #     print(line)
        
        
        # Update active ion section
        for section_title, ion_name in ion_section_titles.items():
            if section_title in line:
                # active_ion = ion_name.replace(" ", "")  # ArIII, ArIV, ...
                active_ion = ion_name
                if active_ion:
                    print(f"Found section: {section_title}")
        
        # Check if the line is a line type header
        for line_type in spectral_lines.keys():
            if line_type in line:
                current_line_type = line_type
        search = True
        line_decomposed = []
        line_step = line
        if "/H20851" in line_step:
                line_step = line_step.replace("/H20851", "")
        if "/H20852" in line_step:
                line_step = line_step.replace("/H20852", "")
        while search:
            matches = {
                1: re.match(r"^\s*(\d+)\s+(.*)$", line_step),
                2: re.match(r"^\s*([\d.]+)\s+(.*)$", line_step),
            }
            if not any(matches.values()):
                search = False
            else:
                match_index = np.array(list(matches.keys()))[np.array(list(matches.values())) != None].max()
                match = matches[match_index]
                if match:
                    line_decomposed.append(match.group(1))
                    line_step = match.group(2)
                else:
                    search = False
        
        
        if active_ion and current_line_type in spectral_lines.keys() and len(line_decomposed) >= 2:
            print(f'Processing line: {j} in page {i + 1}')
            print(f"Line decomposed: {line_decomposed}")
            wavelength = line_decomposed[0]
            wavenumber_calc = 1 / (float(wavelength) * 1e-8) # Convert wavelength to wavenumber in cm^-1
            wavenumber = ''.join(line_decomposed[1:])
            Intensity = 0
            try: 
                delta = abs(float(wavenumber) - wavenumber_calc) / wavenumber_calc
                if delta > 0.01:
                    wavenumber = ''.join(line_decomposed[1:-1]) 
                    delta = abs(float(wavenumber) - wavenumber_calc) / wavenumber_calc
                    Intensity = ''.join(line_decomposed[-1:])
                if delta > 0.01:
                    wavelength = ''.join(line_decomposed[:2])
                    wavenumber_calc = 1 / (float(wavelength) * 1e-8)  # Convert wavelength to wavenumber in cm^-1
                    wavenumber = ''.join(line_decomposed[2:])
                    delta = abs(float(wavenumber) - wavenumber_calc) / wavenumber_calc
                    Intensity = 0
                if delta > 0.01:
                    wavenumber = ''.join(line_decomposed[2:-1])
                    Intensity = ''.join(line_decomposed[-1:])
            except ValueError:
                wavelength = ''.join(line_decomposed[:2])
                wavenumber_calc = 1 / (float(wavelength) * 1e-8)  # Convert wavelength to wavenumber in cm^-1
                wavenumber = ''.join(line_decomposed[2:])
                try:
                    delta = abs(float(wavenumber) - wavenumber_calc) / wavenumber_calc
                except ValueError:
                    wavenumber = ''.join(line_decomposed[2:-1])
                    Intensity = ''.join(line_decomposed[-1:])
                    delta = 0
                if delta > 0.01:
                    wavenumber = ''.join(line_decomposed[2:-1])
                    Intensity = ''.join(line_decomposed[-1:])
                    delta = abs(float(wavenumber) - wavenumber_calc) / wavenumber_calc

                if delta > 0.01:
                    wavelength = ''.join(line_decomposed[:3])
                    wavenumber_calc = 1 / (float(wavelength) * 1e-8)  # Convert wavelength to wavenumber in cm^-1
                    wavenumber = ''.join(line_decomposed[3:])
                    delta = abs(float(wavenumber) - wavenumber_calc) / wavenumber_calc
                    Intensity = 0
                if delta > 0.01:
                    wavenumber = ''.join(line_decomposed[3:-1])
                    Intensity = ''.join(line_decomposed[-1:])
                    
            
            # Append the spectral line information
            spectral_lines[current_line_type].append(
                f"{Intensity:<7}    {wavelength:<10}    {active_ion}    EBS"
            )
            
            

                    
                                
# Save results to a new txt file
output_paths = {
    "Air": "ArLines_Air.txt",
    "Vacuum": "ArLines_Vacuum.txt"
}

for line_type, output_path in output_paths.items():
    # Write the spectral lines to the file
    with open(output_path, 'w') as f:
        for line in spectral_lines[line_type]:
            f.write(line + "\n")