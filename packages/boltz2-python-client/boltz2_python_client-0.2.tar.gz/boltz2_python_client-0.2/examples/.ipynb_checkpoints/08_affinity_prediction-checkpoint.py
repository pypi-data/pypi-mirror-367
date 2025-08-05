#!/usr/bin/env python3
# ---------------------------------------------------------------
# Copyright (c) 2025, NVIDIA CORPORATION. All rights reserved.
# ---------------------------------------------------------------

"""
Example 8: Affinity Prediction

This example demonstrates how to use the new affinity prediction capabilities
in Boltz-2. Affinity prediction estimates the binding affinity (IC50) between
a protein and ligand.

Key points:
- Only one ligand per request can have affinity prediction enabled
- Affinity prediction adds computational time but provides binding estimates
- Results include log(IC50), pIC50, and binary binding probability
"""

import asyncio
import json
from boltz2_client import Boltz2Client, Polymer, Ligand, PredictionRequest

# Protein-ligand example: Kinase protein with Y7W ligand
# This is a protein kinase sequence (272 residues) that binds to the Y7W inhibitor
KINASE_SEQUENCE = """GMGLGYGSWEIDPKDLTFLKELGTGQFGVVKYGKWRGQYDVAIKMIKEGSMSEDEFIEEAKVMMNLSHEKLVQLYGVCTKQRPIFIITEYMANGCLLNYLREMRHRFQTQQLLEMCKDVCEAMEYLESKQFLHRDLAARNCLVNDQGVVKVSDFGLSRYVLDDEYTSSVGSKFPVRWSPPEVLMYSKFSSKSDIWAFGVLMWEIYSLGKMPYERFTNSETAEHIAQGLRLYRPHLASEKVYTIMYSCWHEKADERPTFKILLSNILDVMDEES"""

# Remove newlines and spaces from sequence
KINASE_SEQUENCE = ''.join(KINASE_SEQUENCE.split())

# Y7W ligand CCD code
# Y7W is a kinase inhibitor compound from the Chemical Component Dictionary
LIGAND_CCD = "Y7W"


async def predict_affinity():
    """Demonstrate affinity prediction with protein-ligand complex."""
    # Initialize client
    client = Boltz2Client(base_url="http://localhost:8000")
    
    # Create protein
    protein = Polymer(
        id="A",
        molecule_type="protein",
        sequence=KINASE_SEQUENCE
    )
    
    # Create ligand with affinity prediction enabled
    ligand = Ligand(
        id="Y7W",
        ccd=LIGAND_CCD,  # Using CCD code instead of SMILES
        predict_affinity=True  # Enable affinity prediction
    )
    
    print("🔬 Predicting structure and affinity for Kinase-Y7W complex...")
    print(f"Protein: Kinase ({len(KINASE_SEQUENCE)} residues)")
    print(f"Ligand: {LIGAND_CCD} (CCD code)")
    print("\nNote: Affinity prediction enabled - this will take additional time\n")
    
    # Create prediction request
    request = PredictionRequest(
        polymers=[protein],
        ligands=[ligand],
        # Affinity-specific parameters
        sampling_steps_affinity=200,  # Default: 200
        diffusion_samples_affinity=5,  # Default: 5
        affinity_mw_correction=False,  # Default: False
        # Structure prediction parameters
        sampling_steps=50,
        diffusion_samples=1
    )
    
    # Predict structure with affinity
    result = await client.predict(request)
    
    # Display structure prediction results
    print("✅ Structure prediction complete!")
    print(f"Confidence score: {result.confidence_scores[0]:.3f}")
    
    # Display affinity prediction results
    if result.affinities and "Y7W" in result.affinities:
        affinity = result.affinities["Y7W"]
        
        print("\n📊 Affinity Prediction Results:")
        print("-" * 50)
        
        # Overall predictions
        print(f"Log(IC50): {affinity.affinity_pred_value[0]:.3f}")
        print(f"pIC50: {affinity.affinity_pic50[0]:.3f}")
        print(f"Binary binding probability: {affinity.affinity_probability_binary[0]:.3f}")
        
        # Model-specific predictions
        print("\n📈 Model-specific predictions:")
        print(f"Model 1 - Log(IC50): {affinity.model_1_affinity_pred_value[0]:.3f}")
        print(f"Model 1 - Binary probability: {affinity.model_1_affinity_probability_binary[0]:.3f}")
        print(f"Model 2 - Log(IC50): {affinity.model_2_affinity_pred_value[0]:.3f}")
        print(f"Model 2 - Binary probability: {affinity.model_2_affinity_probability_binary[0]:.3f}")
        
        # Interpret results
        print("\n💊 Interpretation:")
        # pIC50 = -log10(IC50 in M), so IC50 in M = 10^(-pIC50)
        ic50_nm = 10 ** (-affinity.affinity_pic50[0]) * 1e9  # Convert to nM
        print(f"Estimated IC50: {ic50_nm:.2f} nM")
        
        if affinity.affinity_probability_binary[0] > 0.7:
            print("Strong binding predicted (>70% probability)")
        elif affinity.affinity_probability_binary[0] > 0.5:
            print("Moderate binding predicted (>50% probability)")
        else:
            print("Weak binding predicted (<50% probability)")
    
    # Display additional quality metrics
    if result.ligand_iptm_scores:
        print(f"\n🎯 Protein-ligand interface quality (ipTM): {result.ligand_iptm_scores[0]:.3f}")
    
    # Save structure
    with open("kinase_y7w_with_affinity.cif", "w") as f:
        f.write(result.structures[0].structure)
    print("\n💾 Structure saved as kinase_y7w_with_affinity.cif")
    
    # Save affinity results
    if result.affinities:
        with open("kinase_y7w_affinity.json", "w") as f:
            affinity_data = {
                "ligand_id": "Y7W",
                "ligand_ccd": LIGAND_CCD,
                "predictions": {
                    "log_ic50": affinity.affinity_pred_value[0],
                    "pic50": affinity.affinity_pic50[0],
                    "binding_probability": affinity.affinity_probability_binary[0],
                    "ic50_nm": ic50_nm
                }
            }
            json.dump(affinity_data, f, indent=2)
        print("💾 Affinity results saved as kinase_y7w_affinity.json")


async def compare_with_without_affinity():
    """Compare runtime with and without affinity prediction."""
    import time
    
    client = Boltz2Client(base_url="http://localhost:8000")
    
    # Simple protein-ligand system for comparison
    protein = Polymer(
        id="A",
        molecule_type="protein",
        sequence="MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    )
    
    ligand = Ligand(
        id="LIG",
        smiles="CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        predict_affinity=False
    )
    
    print("\n⏱️  Runtime Comparison:")
    print("-" * 50)
    
    # Without affinity prediction
    request1 = PredictionRequest(
        polymers=[protein],
        ligands=[ligand],
        sampling_steps=50
    )
    start = time.time()
    result1 = await client.predict(request1)
    time1 = time.time() - start
    print(f"Without affinity: {time1:.1f} seconds")
    
    # With affinity prediction
    ligand.predict_affinity = True
    request2 = PredictionRequest(
        polymers=[protein],
        ligands=[ligand],
        sampling_steps=50,
        sampling_steps_affinity=200
    )
    start = time.time()
    result2 = await client.predict(request2)
    time2 = time.time() - start
    print(f"With affinity: {time2:.1f} seconds")
    print(f"Additional time for affinity: {time2-time1:.1f} seconds ({(time2/time1-1)*100:.0f}% increase)")


async def main():
    """Run affinity prediction examples."""
    print("🧬 Boltz-2 Affinity Prediction Example")
    print("=" * 60)
    
    # Run main affinity prediction example
    await predict_affinity()
    
    # Optionally run timing comparison
    print("\n\nWould you like to see a runtime comparison? (May take a few minutes)")
    # await compare_with_without_affinity()


if __name__ == "__main__":
    asyncio.run(main()) 