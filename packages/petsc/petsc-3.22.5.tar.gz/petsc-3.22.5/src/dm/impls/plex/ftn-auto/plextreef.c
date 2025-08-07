#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plextree.c */
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
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetreferencetree_ DMPLEXSETREFERENCETREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetreferencetree_ dmplexsetreferencetree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetreferencetree_ DMPLEXGETREFERENCETREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetreferencetree_ dmplexgetreferencetree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexreferencetreegetchildsymmetry_ DMPLEXREFERENCETREEGETCHILDSYMMETRY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexreferencetreegetchildsymmetry_ dmplexreferencetreegetchildsymmetry
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatedefaultreferencetree_ DMPLEXCREATEDEFAULTREFERENCETREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatedefaultreferencetree_ dmplexcreatedefaultreferencetree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsettree_ DMPLEXSETTREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsettree_ dmplexsettree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgettree_ DMPLEXGETTREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgettree_ dmplexgettree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgettreeparent_ DMPLEXGETTREEPARENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgettreeparent_ dmplexgettreeparent
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplextransfervectree_ DMPLEXTRANSFERVECTREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplextransfervectree_ dmplextransfervectree
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexsetreferencetree_(DM dm,DM ref, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(ref);
*ierr = DMPlexSetReferenceTree(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((ref) ));
}
PETSC_EXTERN void  dmplexgetreferencetree_(DM dm,DM *ref, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool ref_null = !*(void**) ref ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ref);
*ierr = DMPlexGetReferenceTree(
	(DM)PetscToPointer((dm) ),ref);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ref_null && !*(void**) ref) * (void **) ref = (void *)-2;
}
PETSC_EXTERN void  dmplexreferencetreegetchildsymmetry_(DM dm,PetscInt *parent,PetscInt *parentOrientA,PetscInt *childOrientA,PetscInt *childA,PetscInt *parentOrientB,PetscInt *childOrientB,PetscInt *childB, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(childOrientB);
CHKFORTRANNULLINTEGER(childB);
*ierr = DMPlexReferenceTreeGetChildSymmetry(
	(DM)PetscToPointer((dm) ),*parent,*parentOrientA,*childOrientA,*childA,*parentOrientB,childOrientB,childB);
}
PETSC_EXTERN void  dmplexcreatedefaultreferencetree_(MPI_Fint * comm,PetscInt *dim,PetscBool *simplex,DM *ref, int *ierr)
{
PetscBool ref_null = !*(void**) ref ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ref);
*ierr = DMPlexCreateDefaultReferenceTree(
	MPI_Comm_f2c(*(comm)),*dim,*simplex,ref);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ref_null && !*(void**) ref) * (void **) ref = (void *)-2;
}
PETSC_EXTERN void  dmplexsettree_(DM dm,PetscSection parentSection,PetscInt parents[],PetscInt childIDs[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(parentSection);
CHKFORTRANNULLINTEGER(parents);
CHKFORTRANNULLINTEGER(childIDs);
*ierr = DMPlexSetTree(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((parentSection) ),parents,childIDs);
}
PETSC_EXTERN void  dmplexgettree_(DM dm,PetscSection *parentSection,PetscInt *parents[],PetscInt *childIDs[],PetscSection *childSection,PetscInt *children[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool parentSection_null = !*(void**) parentSection ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(parentSection);
PetscBool childSection_null = !*(void**) childSection ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(childSection);
*ierr = DMPlexGetTree(
	(DM)PetscToPointer((dm) ),parentSection,parents,childIDs,childSection,children);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! parentSection_null && !*(void**) parentSection) * (void **) parentSection = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! childSection_null && !*(void**) childSection) * (void **) childSection = (void *)-2;
}
PETSC_EXTERN void  dmplexgettreeparent_(DM dm,PetscInt *point,PetscInt *parent,PetscInt *childID, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(parent);
CHKFORTRANNULLINTEGER(childID);
*ierr = DMPlexGetTreeParent(
	(DM)PetscToPointer((dm) ),*point,parent,childID);
}
PETSC_EXTERN void  dmplextransfervectree_(DM dmIn,Vec vecIn,DM dmOut,Vec vecOut,PetscSF sfRefine,PetscSF sfCoarsen,PetscInt *cidsRefine,PetscInt *cidsCoarsen,PetscBool *useBCs,PetscReal *time, int *ierr)
{
CHKFORTRANNULLOBJECT(dmIn);
CHKFORTRANNULLOBJECT(vecIn);
CHKFORTRANNULLOBJECT(dmOut);
CHKFORTRANNULLOBJECT(vecOut);
CHKFORTRANNULLOBJECT(sfRefine);
CHKFORTRANNULLOBJECT(sfCoarsen);
CHKFORTRANNULLINTEGER(cidsRefine);
CHKFORTRANNULLINTEGER(cidsCoarsen);
*ierr = DMPlexTransferVecTree(
	(DM)PetscToPointer((dmIn) ),
	(Vec)PetscToPointer((vecIn) ),
	(DM)PetscToPointer((dmOut) ),
	(Vec)PetscToPointer((vecOut) ),
	(PetscSF)PetscToPointer((sfRefine) ),
	(PetscSF)PetscToPointer((sfCoarsen) ),cidsRefine,cidsCoarsen,*useBCs,*time);
}
#if defined(__cplusplus)
}
#endif
