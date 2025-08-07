from typing import Union

from pydantic import BaseModel

class Job(BaseModel):
    job_id: int
    min_energy: int
    min_loc: int
    workers: int

class JobOpts(BaseModel):
    job_id: int
    link: str
    price_per_block: int
    qasm: Union[dict, None] = None



