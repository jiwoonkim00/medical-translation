export interface SampleReport {
  id: string;
  title: string;
  language: "en" | "ko";
  text: string;
}

export const SAMPLE_REPORTS: SampleReport[] = [
  {
    id: "chest-ct-en",
    title: "흉부 CT (영문)",
    language: "en",
    text: `CLINICAL INDICATION: Shortness of breath, rule out pulmonary embolism.

TECHNIQUE: CT pulmonary angiography with intravenous contrast. Axial images obtained from lung apices to lung bases.

FINDINGS:
No filling defects are identified within the main, lobar, segmental, or subsegmental pulmonary arteries to exclude pulmonary embolism.

Lungs: There is a 1.2 cm solid nodule in the right upper lobe (series 3, image 45). Additionally, there are scattered small ground-glass opacities bilaterally, predominantly in the lower lobes, measuring up to 5 mm in diameter. No consolidation or pleural effusion.

Heart and Pericardium: The cardiac silhouette is normal in size. No pericardial effusion.

Mediastinum: No mediastinal or hilar lymphadenopathy. The aorta is normal in caliber throughout.

Bones: No acute osseous abnormality.

IMPRESSION:
1. No pulmonary embolism.
2. 1.2 cm solid pulmonary nodule in the right upper lobe. Given the size and morphology, intermediate probability of malignancy per Fleischner Society guidelines. CT follow-up in 3 months is recommended.
3. Bilateral ground-glass opacities in the lower lobes, which may represent early infection, aspiration, or atypical pneumonia. Clinical correlation is recommended.`,
  },
  {
    id: "brain-mri-en",
    title: "뇌 MRI (영문)",
    language: "en",
    text: `CLINICAL INDICATION: Headache, dizziness, rule out intracranial hemorrhage or mass lesion.

TECHNIQUE: MRI brain without and with gadolinium contrast. Sequences include T1, T2, FLAIR, DWI, and post-contrast T1-weighted images.

FINDINGS:
There is no evidence of acute infarction on diffusion-weighted imaging. No restricted diffusion identified.

White Matter: Scattered T2/FLAIR hyperintensities are present in the bilateral periventricular and subcortical white matter, consistent with chronic small vessel ischemic disease (Fazekas grade 2). These are nonspecific but may be related to hypertension or migraine.

Ventricles and Sulci: The ventricles are normal in size. The sulci are prominent for the patient's stated age of 62, suggesting mild generalized cerebral volume loss.

Extra-axial Spaces: No subdural or epidural collections. No midline shift.

Posterior Fossa: The cerebellum and brainstem are unremarkable. The cranial nerves are intact.

Vessels: No large vessel occlusion or significant stenosis on MRA. A 4mm aneurysm is identified at the junction of the right middle cerebral artery bifurcation. This is below the threshold for intervention but requires surveillance imaging.

Post-contrast: No abnormal enhancement to suggest active demyelination, metastasis, or primary mass lesion.

IMPRESSION:
1. No acute intracranial hemorrhage or infarction.
2. Moderate small vessel ischemic disease (Fazekas grade 2).
3. Mild cerebral volume loss consistent with the patient's age.
4. Incidental 4mm right MCA bifurcation aneurysm. Neurosurgical or neurovascular consultation recommended. MRA follow-up in 12 months.`,
  },
  {
    id: "abdomen-ct-en",
    title: "복부 CT (영문)",
    language: "en",
    text: `CLINICAL INDICATION: Abdominal pain, nausea. Evaluate for acute abdominal pathology.

TECHNIQUE: CT abdomen and pelvis with intravenous contrast, portal venous phase.

FINDINGS:
Liver: The liver is normal in size and attenuation. A 2.1 cm hypervascular lesion is identified in hepatic segment VII (series 4, image 67), demonstrating arterial enhancement with washout on portal venous phase, highly suspicious for hepatocellular carcinoma (HCC). No other hepatic lesions identified. No biliary ductal dilation.

Gallbladder: The gallbladder is distended with multiple calculi. The wall is thickened at 5mm with pericholecystic fat stranding, consistent with acute cholecystitis.

Pancreas: The pancreas is homogeneous without ductal dilation or peripancreatic stranding.

Spleen: Normal size and attenuation.

Kidneys: Both kidneys are normal in size and function. A 7mm nonobstructing calculus is noted in the left renal pelvis. No hydronephrosis.

Bowel: No bowel obstruction or free air. The appendix is visualized and normal.

Lymph Nodes: No pathologically enlarged lymph nodes.

IMPRESSION:
1. Acute cholecystitis. Surgical consultation recommended.
2. 2.1 cm hepatic lesion in segment VII with imaging characteristics highly suspicious for hepatocellular carcinoma. Multidisciplinary tumor board discussion and liver biopsy or additional MRI liver with hepatobiliary contrast recommended.
3. Left renal calculus, nonobstructing.`,
  },
];

export function getSampleReport(id: string): SampleReport | undefined {
  return SAMPLE_REPORTS.find((r) => r.id === id);
}
