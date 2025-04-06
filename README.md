# OPD System Manager

## Overview
The OPD System Manager is a Python application designed to help hospitals and clinics manage their outpatient department scheduling with AI-powered triage capabilities. The system uses Google's Gemini AI to analyze patient symptoms and recommend appropriate scheduling priorities and timeslots.

## Features
- AI-powered patient triage using Google Gemini
- Department-specific scheduling recommendations
- Emergency case prioritization
- Appointment time slot generation based on historical data
- Simulation capabilities for testing various patient scenarios

## Requirements
- Python 3.7+
- pandas
- numpy
- Google Generative AI (genai) Python library
- Internet connection for Gemini API access

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/opd-system-manager.git
cd opd-system-manager
```

2. Install dependencies:
```
pip install pandas numpy google-generativeai
```

3. Set up your Google Gemini API key:
   - Obtain an API key from the [Google AI Studio](https://aistudio.google.com/)
   - Replace the placeholder API key in the code with your actual key

## Usage

### Basic Usage
```python
from opd_system_manager import OPDSystemManager

# Initialize the system
opd_manager = OPDSystemManager('path/to/historical_data.csv', 'your_gemini_api_key')

# Get time slot recommendations for a patient
patient_details = {
    'department': 'Cardiology',
    'patient_type': 'Regular',
    'symptoms': 'Chest pain, shortness of breath'
}
recommendations = opd_manager.recommend_time_slots(patient_details)
print(recommendations)
```

### Simulation Testing
```python
# Define test scenarios
test_scenarios = [
    {
        'department': 'Emergency',
        'patient_type': 'Critical',
        'symptoms': 'Chest pain, difficulty breathing'
    },
    {
        'department': 'Cardiology',
        'patient_type': 'Regular',
        'symptoms': 'Routine check-up'
    }
]

# Run simulations
results = opd_manager.simulate_patient_flow(test_scenarios)
print(results)
```

## Departments
The system supports the following departments:
- Cardiology
- Emergency
- ENT-A
- ENT-B
- Endocrinology
- Eye-A
- Eye-B
- Gastro
- Gynae-A
- Gynae-B
- Medical-A
- Medical-B
- Haematelogy
- Medical-C
- Neuro Surgery
- Neurology
- ONCOLOGY

## How It Works

1. **Patient Triage**: When patient details are submitted, the system uses Gemini AI to analyze symptoms and determine urgency.

2. **Time Slot Generation**:
   - For emergency cases, immediate slots are generated
   - For regular appointments, slots are created based on department availability and historical patterns

3. **Recommendations**: The system provides up to 3 recommended time slots with estimated wait times.

## Data Format
The system expects historical OPD data in CSV format with at least the following columns:
- `s.no` - Sequential numbering
- `opd` or `department` - Department name
- `time` - Appointment time in the format `dd-mm-yyyy hh:mm AM/PM`

## Security Considerations
- The current implementation includes an API key directly in the code. For production use, it's recommended to use environment variables or a secure configuration system.
- Ensure patient data is handled in compliance with healthcare privacy regulations (HIPAA, GDPR, etc.)

## License
[Insert your license information here]

## Contributing
[Insert contribution guidelines if applicable]

## Credits
This project utilizes Google's Gemini AI for medical triage assistance.
