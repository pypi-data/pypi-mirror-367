import httpx
import numpy as np


def calculate_rmsd(residuals: np.ndarray) -> float:
    """Calculates root mean square deviation between measurements and fitted model."""
    residuals = np.array(residuals)
    return float(np.sqrt(sum(residuals**2) / len(residuals)))


def pubchem_request_molecule_name(pubchem_cid: int) -> str:
    """Retrieves molecule name from PubChem database based on CID."""

    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{pubchem_cid}/property/Title/JSON"
    response = httpx.get(url)

    if response.status_code == 200:
        res_dict = response.json()
        try:
            molecule_name = res_dict["PropertyTable"]["Properties"][0]["Title"]
            return molecule_name
        except (KeyError, IndexError):
            raise ValueError(
                "Unexpected response structure while retrieving molecule name from PubChem"
            )
    else:
        raise ValueError("Failed to retrieve molecule name from PubChem")
