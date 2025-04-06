import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google import genai
import json
import logging

class OPDSystemManager:
    def __init__(self, historical_data_path, gemini_api_key):
        """
        Initialize OPD system with Gemini AI integration
        
        Parameters:
        - historical_data_path (str): Path to CSV with historical OPD data
        - gemini_api_key (str): Google Gemini API key
        """
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        
        self.historical_data = pd.read_csv(historical_data_path)
        
       
        self.client = genai.Client(api_key=gemini_api_key)
        
        
        self.priority_departments = ['Emergency', 'Cardiology']
        
       
        self.all_departments = [
            'Cardiology', 'Emergency', 'ENT-A', 'ENT-B', 'Endocrinology', 
            'Eye-A', 'Eye-B', 'Gastro', 'Gynae-A', 'Gynae-B', 
            'Medical-A', 'Medical-B', 'Haematelogy', 'Medical-C', 
            'Neuro Surgery', 'Neurology', 'ONCOLOGY'
        ]
    
    def parse_datetime(self, date_str):
        """
        Parse datetime from the specific format: dd-mm-yyyy hour:minute am/pm
        """
        try:
            return datetime.strptime(date_str, '%d-%m-%Y %I:%M %p')
        except ValueError:
            self.logger.error(f"Error parsing date: {date_str}")
            return None
    
    def use_gemini_for_triage(self, patient_details):
        """
        Use Gemini AI to perform initial patient triage
        
        Parameters:
        - patient_details (dict): Patient information
        
        Returns:
        - Triage recommendation
        """
        
        prompt = f"""
        Perform a medical triage assessment based on the following patient details:
        Department: {patient_details.get('department', 'Not specified')}
        Patient Type: {patient_details.get('patient_type', 'Not specified')}
        Symptoms: {patient_details.get('symptoms', 'No symptoms provided')}

        Provide:
        1. Urgency level (Immediate/High/Medium/Low)
        2. Recommended initial actions
        3. Potential department priority
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return {
                'triage_assessment': response.text,
                'raw_response_text': str(response)  # conversion for json serialization 
            }
        except Exception as e:
            return {
                'error': f"Gemini API error: {str(e)}",
                'details': patient_details
            }
    
    def recommend_time_slots(self, patient_details):
        """
        Recommend time slots with Gemini AI insights
        
        Parameters:
        - patient_details (dict): Patient information
        
        Returns:
        - Recommended time slots with AI insights (limited to 3 slots)
        """
        
        department = patient_details.get('department', '')
        if department not in self.all_departments:
            return {
                'error': 'Invalid department',
                'available_departments': self.all_departments
            }
        
        
        triage_result = self.use_gemini_for_triage(patient_details)
        
        
        if department == 'Emergency':
            return self._generate_emergency_slots(patient_details, triage_result)
        
        
        slots = self._generate_regular_slots(patient_details)
        
        
        slots['gemini_triage'] = triage_result
        
        return slots
    
    def _generate_emergency_slots(self, patient_details, triage_result):
        """
        Generate immediate slots for emergency cases (limited to 3)
        """
        now = datetime.now()
        emergency_slots = []
        
        for i in range(3):  # Limited to 3 slots
            slot_time = now + timedelta(minutes=15*i)
            emergency_slots.append({
                'date': slot_time.strftime('%d-%m-%Y'),
                'time': slot_time.strftime('%I:%M %p'),
                'priority': 'HIGH',
                'estimated_wait': 0,
                'notes': 'Emergency priority - Immediate attention required'
            })
        
        return {
            'department': 'Emergency',
            'recommended_slots': emergency_slots,
            'gemini_triage': triage_result
        }
    
    def _generate_regular_slots(self, patient_details):
        """
        Generate time slots for non-emergency departments (limited to 3)
        """
        department = patient_details.get('department')
        
        
        try:
            dept_data = self.historical_data[
                self.historical_data['opd'] == department
            ]
        except KeyError:
            try:
                
                dept_data = self.historical_data[
                    self.historical_data['department'] == department
                ]
            except KeyError:
                
                self.logger.warning(f"No matching column found for department {department}")
                dept_data = pd.DataFrame()
        
        recommended_slots = []
        
        # Create enough potential slots to choose from
        potential_slots = []
        for day_offset in range(3):
            for hour in [9, 10, 11, 14, 15, 16]:
                for minute in [0, 30]:
                    slot_time = datetime.now() + timedelta(days=day_offset)
                    slot_time = slot_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    potential_slots.append({
                        'date': slot_time.strftime('%d-%m-%Y'),
                        'time': slot_time.strftime('%I:%M %p'),
                        'estimated_wait': np.random.randint(15, 60),
                        'department': department
                    })
        
        # Select only 3 slots
        # For realistic scheduling, take the first 3 available slots
        recommended_slots = potential_slots[:3]
        
        return {
            'department': department,
            'recommended_slots': recommended_slots
        }
    
    def simulate_patient_flow(self, test_scenarios):
        """
        Simulate patient scenarios for testing
        
        Parameters:
        - test_scenarios (list): List of patient scenarios to test
        
        Returns:
        - Test results for each scenario
        """
        test_results = []
        
        for scenario in test_scenarios:
            try:
                result = self.recommend_time_slots(scenario)
                test_results.append({
                    'input': scenario,
                    'result': result
                })
            except Exception as e:
                test_results.append({
                    'input': scenario,
                    'error': str(e)
                })
        
        return test_results

def main():
    
    GEMINI_API_KEY = 'AIzaSyAHOaOT-dx28PBk46PBpgvbj9ocDjMAlZ4' 
    
    
    sample_csv_path = 'Patients_Records2.csv'
    
    
    try:
        pd.read_csv(sample_csv_path)
    except FileNotFoundError:
        
        sample_data = pd.DataFrame({
            's.no': range(1, 200),
            'opd': ['Cardiology']*60 + ['Emergency']*40 + ['Neurology']*100,
            'time': [
                f'{day:02d}-{month:02d}-2023 {hour:02d}:{minute:02d} {"AM" if hour < 12 else "PM"}'
                for day in range(1, 31)
                for month in range(1, 13)
                for hour in [9, 10, 11, 14, 15, 16]
                for minute in [0, 30]
            ][:200]
        })
        sample_data.to_csv(sample_csv_path, index=False)
    
    
    opd_manager = OPDSystemManager(sample_csv_path, GEMINI_API_KEY)
    
   
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
        },
        {
            'department': 'Neurology',
            'patient_type': 'Follow-up',
            'symptoms': 'Headache monitoring'
        }
    ]
    
    
    test_results = opd_manager.simulate_patient_flow(test_scenarios)
    
    
    print("Test Scenario Results:")
    print(json.dumps(test_results, indent=2))

if __name__ == "__main__":
    main()