import json
import os
import requests
from pathlib import Path
from typing import List, Dict, Any
from django.conf import settings
from .email_service import send_email

# Define types similar to TypeScript
class AvailabilityItem:
    def __init__(self, available: str, available_date: str):
        self.available = available
        self.available_date = available_date

def get_data() -> Dict[str, Any]:
    """Fetch data from Sanparks API"""
    endpoint = "https://production-sfo.browserless.io/chrome/bql"
    token = os.environ.get('BROWSERLESS_TOKEN', '')
    proxy_string = "&proxy=residential&proxySticky=true&proxyCountry=us"
    options_string = "&humanlike=true&blockConsentModals=true"
    
    options = {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
        },
        "json": {
            "query": """
                mutation form_example {
                  goto(
                    url: "https://www.sanparks.org/includes/SANParksApp/API/v1/bookings/activities/getActivityDetails.php?accomTypeNo=396"
                  ) {
                    text
                  }
                  query: querySelector(selector: "body") {
                    innerText
                  }
                }
            """,
            "operationName": "form_example",
        }
    }
    
    url = f"{endpoint}?token={token}{proxy_string}{options_string}"
    response = requests.post(url, json=options["json"], headers=options["headers"])
    return response.json()

def get_availability() -> List[AvailabilityItem]:
    """Get availability data and parse it"""
    data = get_data()
    res = json.loads(data['data']['query']['innerText'])
    availability = res['DATA'][0]['availability']
    
    
    availability_array = []
    for item in availability.values():
        print(item)
        availability_array.append(AvailabilityItem(
            available=item['available'],
            available_date=item['availableDate']
        ))
    
    return availability_array

def find_difference_indices(old: str, new: str) -> List[int]:
    """Find differences between old and new availability"""
    diff_indices = []

    old = old.split(",") 
    new = new.split(",")    
    
    old = old[len(old) - len(new):] #this is the case where the new is shorter than the old, since it is a new day, the api returns less days
    
    for i in range(len(old)):
        new_el = int(new[i])
        old_el = int(old[i])
        change_availability = new_el - old_el
        diff_indices.append(change_availability if change_availability > 0 else 0)
    
    return diff_indices

def create_message(diff_indices: List[int], availability_array: List[AvailabilityItem]) -> str:
    """Create HTML message for email notification"""
    available_string = ""
    first_available_date = ""
    
    for i in range(len(diff_indices)):
        if diff_indices[i] > 0:
            available_string += f"<p>{diff_indices[i]} new spots available on {availability_array[i].available_date}.</p>\r\n"
            if not first_available_date:
                first_available_date = availability_array[i].available_date
    
    return f"""
    <div>
      <p>The following dates have recently become available for Otter Trail: </p>
      {available_string}
      <p>Click <a href="https://www.sanparks.org/reservations/overnight-activity-details/396/1/{first_available_date}">here</a> to book.</p>
    </div>
    """

def check_availability():
    """Main function to check availability and send notifications"""
    try:
        availability = get_availability()
        neww = ','.join(item.available for item in availability)
        
        # Get the path to lastScrap.txt
        file_path = Path(settings.BASE_DIR) / 'scrap_monitor' / 'last_scrap.txt'
        
        # Read the last availability data
        if file_path.exists():
            with open(file_path, 'r') as f:
                old = f.read().strip()
        else:
            # If file doesn't exist, create it with current availability
            with open(file_path, 'w') as f:
                f.write(neww)
            return
        
        # Find differences
        diff_indices = find_difference_indices(old, neww)
        
        # If there are new availabilities, update the file and send email
        if any(index > 0 for index in diff_indices):
            with open(file_path, 'w') as f:
                f.write(neww)
            
            message = create_message(diff_indices, availability)
            send_email(['camgadams@gmail.com'], message)
            
            return True, message
        
        return False, None
    
    except Exception as err:
        error_message = f"Scraping failed: {err}"
        send_email(['camgadams@gmail.com'], error_message)
        return False, error_message


def test():
    old = "0,12,0,0,0,0,0,0,0,0,0,0,0,0,12,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
    neww = "12,0,0,0,0,0,0,0,0,0,0,0,0,12,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"

    # print(len(old.split(",")))
    # print(len(new.split(",")))
    
    res = find_difference_indices(old, neww)
    
    print(res)
    
test()