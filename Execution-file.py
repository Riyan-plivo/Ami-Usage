import boto3
import csv

regions = ['us-west-1', 'us-east-1', 'ap-south-1']

aws_man_console = boto3.session.Session(profile_name="default")

# Here using the AMI-ID to store all the AMI-ID
ami_data = {}

for region in regions:
    print(f"\nChecking region: {region}")
    
    # Creating a client ec2 in the specified region (Checking all the instances in that region)
    ec2_console = aws_man_console.client(service_name="ec2", region_name=region)
    
    # Describe instances is used to , to depict about all the instances running/stopped in that particular region
    res = ec2_console.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running', 'stopped']},
        ]
    )
    # Reservations is the outer sections and we are carrying one reservation and accessing details regarding particular instances
    for x in res['Reservations']:
        for c in x['Instances']:
            ami_id = c['ImageId']
            instance_id = c['InstanceId']
            instance_type = c['InstanceType']
            instance_state = c['State']['Name']
            instance_name = ''
            
            # Accessing instance name from tags , that instances have.
            if 'Tags' in c:
                for tag in c['Tags']:
                    if tag['Key'] == 'Name':
                        instance_name = tag['Value']
                        break

            instance_detail = f"{instance_name} ({instance_id})"
            
            # If the AMI-ID is already in the dictionary, update its entry
            if ami_id in ami_data:
                ami_data[ami_id]['InstanceCount'] += 1
                if instance_state == 'running':
                    ami_data[ami_id]['RunningCount'] += 1
                    ami_data[ami_id]['Instance-ID-Running'].append(instance_detail)
                elif instance_state == 'stopped':
                    ami_data[ami_id]['StoppedCount'] += 1
                    ami_data[ami_id]['Instance-ID-Stopped'].append(instance_detail)
            else:
                # If it's a new AMI-ID, add it to the dictionary
                ami_data[ami_id] = {
                    'Region': region,
                    'InstanceCount': 1,
                    'RunningCount': 1 if instance_state == 'running' else 0,
                    'StoppedCount': 1 if instance_state == 'stopped' else 0,
                    'Instance-ID-Running': [instance_detail] if instance_state == 'running' else [],
                    'Instance-ID-Stopped': [instance_detail] if instance_state == 'stopped' else []
                }

# Writing the collected data to a CSV file (ami_instances.csv)
with open('ami_instances.csv', mode='w', newline='') as csv_file:
    fieldnames = ['AMI-ID', 'Region', 'InstanceCount', 'RunningCount', 'StoppedCount', 'Instance-ID-Running', 'Instance-ID-Stopped']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    writer.writeheader()
    for ami_id, data in ami_data.items():
        writer.writerow({
            'AMI-ID': ami_id,
            'Region': data['Region'],
            'InstanceCount': data['InstanceCount'],
            'RunningCount': data['RunningCount'],
            'StoppedCount': data['StoppedCount'],
            'Instance-ID-Running': ', '.join(data['Instance-ID-Running']),
            'Instance-ID-Stopped': ', '.join(data['Instance-ID-Stopped'])
        })

print("Data is written in the csv file .")
