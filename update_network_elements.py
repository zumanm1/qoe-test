"""
Script to update network elements and subdomains in the Mobile QoE Tool database
This will add the three IP-MPLS subdomains and network elements for each domain as specified
"""
from app import create_app, db
from app.models.network import NetworkElement
from app.models.subdomain import NetworkSubdomain

app = create_app()

with app.app_context():
    # First clean up existing subdomains and elements to avoid duplicates
    print("Removing existing subdomains and elements...")
    NetworkElement.query.delete()
    NetworkSubdomain.query.delete()
    db.session.commit()
    
    # Create subdomains for Transport domain
    print("Creating new subdomains...")
    subdomains = [
        NetworkSubdomain(
            subdomain_name="IP-MPLS_Backhaul",
            parent_domain="transport",
            description="Connects RAN side via IP VRF to the Core Data Network using Inter-AS Option A"
        ),
        NetworkSubdomain(
            subdomain_name="IP-MPLS_CoreDataNetwork",
            parent_domain="transport",
            description="Provides connectivity between Core Network elements (S-GW, P-GW, IGW)"
        ),
        NetworkSubdomain(
            subdomain_name="IP-MPLS_International",
            parent_domain="transport",
            description="Provides connectivity to external networks and internet"
        )
    ]
    db.session.add_all(subdomains)
    db.session.commit()
    
    # Add network elements for each domain
    print("Creating network elements...")
    
    # RAN Domain elements
    ran_elements = [
        NetworkElement(
            element_name="UE_1",
            element_type="User Equipment",
            domain="ran",
            status="active",
            location="End User"
        ),
        NetworkElement(
            element_name="eNodeB_1",
            element_type="Base Station",
            domain="ran",
            status="active",
            location="Cell Site 1"
        ),
        NetworkElement(
            element_name="eNodeB_2",
            element_type="Base Station",
            domain="ran",
            status="active",
            location="Cell Site 2"
        )
    ]
    
    # Transport Domain elements - IP-MPLS Backhaul
    backhaul_elements = [
        NetworkElement(
            element_name="PE11",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_Backhaul",
            status="active",
            location="Backhaul Edge 1"
        ),
        NetworkElement(
            element_name="P10",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_Backhaul",
            status="active",
            location="Backhaul Core 1"
        ),
        NetworkElement(
            element_name="PE12",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_Backhaul",
            status="active",
            location="Backhaul Edge 2"
        )
    ]
    
    # Transport Domain elements - IP-MPLS Core Data Network
    core_data_elements = [
        NetworkElement(
            element_name="PEyy1",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_CoreDataNetwork",
            status="active",
            location="Core Data Network Edge 1"
        ),
        NetworkElement(
            element_name="Pyy0",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_CoreDataNetwork",
            status="active",
            location="Core Data Network Core"
        ),
        NetworkElement(
            element_name="PEyy2",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_CoreDataNetwork",
            status="active",
            location="Core Data Network Edge 2"
        )
    ]
    
    # Transport Domain elements - IP-MPLS International/Internet
    international_elements = [
        NetworkElement(
            element_name="PE1",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_International",
            status="active",
            location="International Edge 1"
        ),
        NetworkElement(
            element_name="P0",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_International",
            status="active",
            location="International Core"
        ),
        NetworkElement(
            element_name="PE2",
            element_type="router",
            domain="transport",
            subdomain="IP-MPLS_International",
            status="active",
            location="International Edge 2"
        )
    ]
    
    # Core Domain elements
    core_elements = [
        NetworkElement(
            element_name="MME",
            element_type="Mobility Management Entity",
            domain="core",
            status="active",
            location="Core Network"
        ),
        NetworkElement(
            element_name="HSS",
            element_type="Home Subscriber Server",
            domain="core",
            status="active",
            location="Core Network"
        ),
        NetworkElement(
            element_name="PCRF",
            element_type="Policy and Charging Rules Function",
            domain="core",
            status="active",
            location="Core Network"
        ),
        NetworkElement(
            element_name="S-GW",
            element_type="Serving Gateway",
            domain="core",
            status="active",
            location="Core Network"
        ),
        NetworkElement(
            element_name="P-GW",
            element_type="PDN Gateway",
            domain="core",
            status="active",
            location="Core Network"
        ),
        NetworkElement(
            element_name="IGW",
            element_type="Internet Gateway",
            domain="core",
            status="active",
            location="Core Network"
        )
    ]
    
    # Internet Domain elements
    internet_elements = [
        NetworkElement(
            element_name="INS PE1",
            element_type="router",
            domain="internet",
            status="active",
            location="Internet POP 1"
        ),
        NetworkElement(
            element_name="INS P0",
            element_type="router",
            domain="internet",
            status="active",
            location="Internet Core"
        ),
        NetworkElement(
            element_name="INS PE2",
            element_type="router",
            domain="internet",
            status="active",
            location="Internet POP 2"
        ),
        NetworkElement(
            element_name="Ookla Server",
            element_type="Speed Test Server",
            domain="internet",
            status="active",
            location="Data Center"
        )
    ]
    
    # Add all elements to the database
    all_elements = ran_elements + backhaul_elements + core_data_elements + international_elements + core_elements + internet_elements
    db.session.add_all(all_elements)
    db.session.commit()
    
    print("Database updated successfully!")
    print(f"Created {len(subdomains)} subdomains and {len(all_elements)} network elements")
