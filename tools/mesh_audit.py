"""Small dependency-free triangle OBJ audit. Measurements, not full geometry certification."""
import argparse
from collections import Counter,defaultdict
import json
import math
from pathlib import Path

def load_obj(path):
    vertices=[]; faces=[]
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        words=line.split()
        if not words or words[0].startswith("#"): continue
        if words[0]=="v":
            if len(words)!=4: raise ValueError("Require 3D vertices")
            point=tuple(float(x) for x in words[1:])
            if not all(math.isfinite(x) for x in point): raise ValueError("Non-finite vertex")
            vertices.append(point)
        elif words[0]=="f":
            if len(words)!=4: raise ValueError("Only triangle faces accepted")
            face=tuple(int(x.split("/")[0])-1 for x in words[1:])
            if any(i<0 or i>=len(vertices) for i in face): raise ValueError("Invalid vertex index")
            faces.append(face)
    if not vertices or not faces: raise ValueError("Empty mesh")
    return vertices,faces

def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def subtract(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))

def audit(vertices,faces,scale_to_mm=1):
    if not math.isfinite(scale_to_mm) or scale_to_mm<=0: raise ValueError("Scale must be finite and positive")
    vertices=[tuple(scale_to_mm*x for x in p) for p in vertices]
    edge_faces=defaultdict(list); used=set(); face_counts=Counter(); degenerate=0; area=0; signed_volume=0
    parent=list(range(len(faces)))
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[a]=b
    for fi,f in enumerate(faces):
        used.update(f);face_counts[tuple(sorted(f))]+=1
        p,q,r=(vertices[i] for i in f)
        normal=cross(subtract(q,p),subtract(r,p)); tri_area=math.sqrt(dot(normal,normal))/2
        if len(set(f))<3 or tri_area<=1e-12: degenerate+=1
        area+=tri_area;signed_volume+=dot(p,cross(q,r))/6
        for a,b in zip(f,(f[1],f[2],f[0])):
            edge=tuple(sorted((a,b)))
            for old,_ in edge_faces[edge]: union(fi,old)
            edge_faces[edge].append((fi,1 if a<b else -1))
    boundary=sum(len(v)==1 for v in edge_faces.values())
    nonmanifold=sum(len(v)>2 or k[0]==k[1] for k,v in edge_faces.items())
    inconsistent=sum(len(v)==2 and sum(direction for _,direction in v)!=0 for v in edge_faces.values())
    duplicates=sum(n-1 for n in face_counts.values())
    min_xyz=[min(vertices[i][axis] for i in used) for axis in range(3)]
    max_xyz=[max(vertices[i][axis] for i in used) for axis in range(3)]
    topologically_closed=not(boundary or nonmanifold or degenerate or duplicates or inconsistent)
    return {"vertices_used":len(used),"triangles":len(faces),"edges":len(edge_faces),
      "face_edge_components":len({find(i) for i in range(len(faces))}),"boundary_edges":boundary,
      "nonmanifold_edges":nonmanifold,"inconsistent_winding_edges":inconsistent,
      "duplicate_triangles":duplicates,"degenerate_triangles":degenerate,
      "euler_characteristic":len(used)-len(edge_faces)+len(faces),
      "bbox_min_mm":min_xyz,"bbox_max_mm":max_xyz,"bbox_size_mm":[b-a for a,b in zip(min_xyz,max_xyz)],
      "surface_area_mm2":area,"signed_volume_mm3":signed_volume,
      "volume_usable_for_closed_oriented_mesh_only":topologically_closed,
      "self_intersection_checked":False,"surface_fidelity_checked":False,"not_a_complete_acceptance":True}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("obj",type=Path);parser.add_argument("--scale-to-mm",type=float,default=1)
    args=parser.parse_args()
    print(json.dumps(audit(*load_obj(args.obj),args.scale_to_mm),indent=2))
if __name__=="__main__": main()
