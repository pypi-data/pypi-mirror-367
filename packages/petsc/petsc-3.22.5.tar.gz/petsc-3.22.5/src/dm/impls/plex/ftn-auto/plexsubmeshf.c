#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexsubmesh.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplex.h"
#include "petscdmlabel.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexmarkboundaryfaces_ DMPLEXMARKBOUNDARYFACES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexmarkboundaryfaces_ dmplexmarkboundaryfaces
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlabelcomplete_ DMPLEXLABELCOMPLETE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlabelcomplete_ dmplexlabelcomplete
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlabeladdcells_ DMPLEXLABELADDCELLS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlabeladdcells_ dmplexlabeladdcells
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlabeladdfacecells_ DMPLEXLABELADDFACECELLS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlabeladdfacecells_ dmplexlabeladdfacecells
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlabelclearcells_ DMPLEXLABELCLEARCELLS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlabelclearcells_ dmplexlabelclearcells
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexconstructghostcells_ DMPLEXCONSTRUCTGHOSTCELLS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexconstructghostcells_ dmplexconstructghostcells
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexlabelcohesivecomplete_ DMPLEXLABELCOHESIVECOMPLETE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexlabelcohesivecomplete_ dmplexlabelcohesivecomplete
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatehybridmesh_ DMPLEXCREATEHYBRIDMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatehybridmesh_ dmplexcreatehybridmesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetorientedface_ DMPLEXGETORIENTEDFACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetorientedface_ dmplexgetorientedface
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatesubmesh_ DMPLEXCREATESUBMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatesubmesh_ dmplexcreatesubmesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatecohesivesubmesh_ DMPLEXCREATECOHESIVESUBMESH
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatecohesivesubmesh_ dmplexcreatecohesivesubmesh
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexreordercohesivesupports_ DMPLEXREORDERCOHESIVESUPPORTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexreordercohesivesupports_ dmplexreordercohesivesupports
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexfilter_ DMPLEXFILTER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexfilter_ dmplexfilter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetsubpointmap_ DMPLEXGETSUBPOINTMAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetsubpointmap_ dmplexgetsubpointmap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetsubpointmap_ DMPLEXSETSUBPOINTMAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetsubpointmap_ dmplexsetsubpointmap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetsubpointis_ DMPLEXGETSUBPOINTIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetsubpointis_ dmplexgetsubpointis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetenclosurerelation_ DMGETENCLOSURERELATION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetenclosurerelation_ dmgetenclosurerelation
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmgetenclosurepoint_ DMGETENCLOSUREPOINT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmgetenclosurepoint_ dmgetenclosurepoint
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexmarkboundaryfaces_(DM dm,PetscInt *val,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
*ierr = DMPlexMarkBoundaryFaces(
	(DM)PetscToPointer((dm) ),*val,
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmplexlabelcomplete_(DM dm,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
*ierr = DMPlexLabelComplete(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmplexlabeladdcells_(DM dm,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
*ierr = DMPlexLabelAddCells(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmplexlabeladdfacecells_(DM dm,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
*ierr = DMPlexLabelAddFaceCells(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmplexlabelclearcells_(DM dm,DMLabel label, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
*ierr = DMPlexLabelClearCells(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ));
}
PETSC_EXTERN void  dmplexconstructghostcells_(DM dm, char labelName[],PetscInt *numGhostCells,DM *dmGhosted, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(numGhostCells);
PetscBool dmGhosted_null = !*(void**) dmGhosted ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmGhosted);
/* insert Fortran-to-C conversion for labelName */
  FIXCHAR(labelName,cl0,_cltmp0);
*ierr = DMPlexConstructGhostCells(
	(DM)PetscToPointer((dm) ),_cltmp0,numGhostCells,dmGhosted);
  FREECHAR(labelName,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmGhosted_null && !*(void**) dmGhosted) * (void **) dmGhosted = (void *)-2;
}
PETSC_EXTERN void  dmplexlabelcohesivecomplete_(DM dm,DMLabel label,DMLabel blabel,PetscInt *bvalue,PetscBool *flip,PetscBool *split,DM subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(blabel);
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMPlexLabelCohesiveComplete(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),
	(DMLabel)PetscToPointer((blabel) ),*bvalue,*flip,*split,
	(DM)PetscToPointer((subdm) ));
}
PETSC_EXTERN void  dmplexcreatehybridmesh_(DM dm,DMLabel label,DMLabel bdlabel,PetscInt *bdvalue,DMLabel *hybridLabel,DMLabel *splitLabel,DM *dmInterface,DM *dmHybrid, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(label);
CHKFORTRANNULLOBJECT(bdlabel);
PetscBool hybridLabel_null = !*(void**) hybridLabel ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(hybridLabel);
PetscBool splitLabel_null = !*(void**) splitLabel ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(splitLabel);
PetscBool dmInterface_null = !*(void**) dmInterface ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmInterface);
PetscBool dmHybrid_null = !*(void**) dmHybrid ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmHybrid);
*ierr = DMPlexCreateHybridMesh(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((label) ),
	(DMLabel)PetscToPointer((bdlabel) ),*bdvalue,hybridLabel,splitLabel,dmInterface,dmHybrid);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! hybridLabel_null && !*(void**) hybridLabel) * (void **) hybridLabel = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! splitLabel_null && !*(void**) splitLabel) * (void **) splitLabel = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmInterface_null && !*(void**) dmInterface) * (void **) dmInterface = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmHybrid_null && !*(void**) dmHybrid) * (void **) dmHybrid = (void *)-2;
}
PETSC_EXTERN void  dmplexgetorientedface_(DM dm,PetscInt *cell,PetscInt *faceSize, PetscInt face[],PetscInt *numCorners,PetscInt indices[],PetscInt origVertices[],PetscInt faceVertices[],PetscBool *posOriented, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(face);
CHKFORTRANNULLINTEGER(indices);
CHKFORTRANNULLINTEGER(origVertices);
CHKFORTRANNULLINTEGER(faceVertices);
*ierr = DMPlexGetOrientedFace(
	(DM)PetscToPointer((dm) ),*cell,*faceSize,face,*numCorners,indices,origVertices,faceVertices,posOriented);
}
PETSC_EXTERN void  dmplexcreatesubmesh_(DM dm,DMLabel vertexLabel,PetscInt *value,PetscBool *markedFaces,DM *subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(vertexLabel);
PetscBool subdm_null = !*(void**) subdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMPlexCreateSubmesh(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((vertexLabel) ),*value,*markedFaces,subdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subdm_null && !*(void**) subdm) * (void **) subdm = (void *)-2;
}
PETSC_EXTERN void  dmplexcreatecohesivesubmesh_(DM dm,PetscBool *hasLagrange, char label[],PetscInt *value,DM *subdm, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
PetscBool subdm_null = !*(void**) subdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subdm);
/* insert Fortran-to-C conversion for label */
  FIXCHAR(label,cl0,_cltmp0);
*ierr = DMPlexCreateCohesiveSubmesh(
	(DM)PetscToPointer((dm) ),*hasLagrange,_cltmp0,*value,subdm);
  FREECHAR(label,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subdm_null && !*(void**) subdm) * (void **) subdm = (void *)-2;
}
PETSC_EXTERN void  dmplexreordercohesivesupports_(DM dm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexReorderCohesiveSupports(
	(DM)PetscToPointer((dm) ));
}
PETSC_EXTERN void  dmplexfilter_(DM dm,DMLabel cellLabel,PetscInt *value,PetscBool *ignoreLabelHalo,PetscBool *sanitizeSubmesh,PetscSF *ownershipTransferSF,DM *subdm, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(cellLabel);
PetscBool ownershipTransferSF_null = !*(void**) ownershipTransferSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ownershipTransferSF);
PetscBool subdm_null = !*(void**) subdm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subdm);
*ierr = DMPlexFilter(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((cellLabel) ),*value,*ignoreLabelHalo,*sanitizeSubmesh,ownershipTransferSF,subdm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ownershipTransferSF_null && !*(void**) ownershipTransferSF) * (void **) ownershipTransferSF = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subdm_null && !*(void**) subdm) * (void **) subdm = (void *)-2;
}
PETSC_EXTERN void  dmplexgetsubpointmap_(DM dm,DMLabel *subpointMap, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool subpointMap_null = !*(void**) subpointMap ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subpointMap);
*ierr = DMPlexGetSubpointMap(
	(DM)PetscToPointer((dm) ),subpointMap);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subpointMap_null && !*(void**) subpointMap) * (void **) subpointMap = (void *)-2;
}
PETSC_EXTERN void  dmplexsetsubpointmap_(DM dm,DMLabel subpointMap, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(subpointMap);
*ierr = DMPlexSetSubpointMap(
	(DM)PetscToPointer((dm) ),
	(DMLabel)PetscToPointer((subpointMap) ));
}
PETSC_EXTERN void  dmplexgetsubpointis_(DM dm,IS *subpointIS, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool subpointIS_null = !*(void**) subpointIS ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subpointIS);
*ierr = DMPlexGetSubpointIS(
	(DM)PetscToPointer((dm) ),subpointIS);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subpointIS_null && !*(void**) subpointIS) * (void **) subpointIS = (void *)-2;
}
PETSC_EXTERN void  dmgetenclosurerelation_(DM dmA,DM dmB,DMEnclosureType *rel, int *ierr)
{
CHKFORTRANNULLOBJECT(dmA);
CHKFORTRANNULLOBJECT(dmB);
*ierr = DMGetEnclosureRelation(
	(DM)PetscToPointer((dmA) ),
	(DM)PetscToPointer((dmB) ),rel);
}
PETSC_EXTERN void  dmgetenclosurepoint_(DM dmA,DM dmB,DMEnclosureType *etype,PetscInt *pB,PetscInt *pA, int *ierr)
{
CHKFORTRANNULLOBJECT(dmA);
CHKFORTRANNULLOBJECT(dmB);
CHKFORTRANNULLINTEGER(pA);
*ierr = DMGetEnclosurePoint(
	(DM)PetscToPointer((dmA) ),
	(DM)PetscToPointer((dmB) ),*etype,*pB,pA);
}
#if defined(__cplusplus)
}
#endif
