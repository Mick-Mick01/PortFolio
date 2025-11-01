from pathlib import Path

# Always resolves relative to this file, not to where Python is run
current_dir = Path(__file__).resolve().parent
route_txt_path = current_dir.parent / "conflict_files" / "route.txt"
collection_txt_path = current_dir.parent / "conflict_files" / "collection.txt"


def check_conflicts(new_route_name, collection_name):
    with open(route_txt_path, 'r') as f:
        routes = list(f)
        for route in routes:
            if (new_route_name+"\n" == route):
                return False
        with open(route_txt_path, 'a') as a:
            a.write(f"{new_route_name}\n")
    
    
    with open(collection_txt_path, 'r') as f:
        collections = list(f)
        for collection in collections:
            if (collection_name+"\n" == collection):
                return False
        with open(collection_txt_path, 'a') as a:
            a.write(f"{collection_name}\n")
            
    return True
        
def check_conflicting_route(new_route_name):
    with open(route_txt_path, 'r') as f:
        routes = list(f)
        for route in routes:
            if (new_route_name+"\n" == route):
                return False
        with open(route_txt_path, 'a') as a:
            a.write(f"{new_route_name}\n")
            
    return True


def check_conflicting_collection(collection_name):
    with open(collection_txt_path, 'r') as f:
        collections = list(f)
        for collection in collections:
            if (collection_name+"\n" == collection):
                return False
        with open(collection_txt_path, 'a') as a:
            a.write(f"{collection_name}\n")
            
    return True