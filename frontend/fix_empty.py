import os

directory = 'c:/Users/dhira/OneDrive/Desktop/CEP SEM4/1st attempt/ARA-1-Financial-Agent/VJTI_HACKATHON/frontend/src/pages'
for f in os.listdir(directory):
    if f.endswith('.jsx'):
        path = os.path.join(directory, f)
        if os.path.getsize(path) == 0:
            name = f[:-4]
            content = f"""import React from 'react';

const {name} = () => {{
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold">{name}</h1>
    </div>
  );
}};

export default {name};
"""
            with open(path, 'w') as file:
                file.write(content)
            print(f"Fixed {f}")
