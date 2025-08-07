#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* sfutils.c */
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

#include "petscsf.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsetgraphlayout_ PETSCSFSETGRAPHLAYOUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsetgraphlayout_ petscsfsetgraphlayout
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfsetgraphsection_ PETSCSFSETGRAPHSECTION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfsetgraphsection_ petscsfsetgraphsection
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfcreatebymatchingindices_ PETSCSFCREATEBYMATCHINGINDICES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfcreatebymatchingindices_ petscsfcreatebymatchingindices
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfmerge_ PETSCSFMERGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfmerge_ petscsfmerge
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsfcreatestridedsf_ PETSCSFCREATESTRIDEDSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsfcreatestridedsf_ petscsfcreatestridedsf
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsfsetgraphlayout_(PetscSF sf,PetscLayout layout,PetscInt *nleaves,PetscInt *ilocal,PetscCopyMode *localmode, PetscInt *gremote, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(layout);
CHKFORTRANNULLINTEGER(ilocal);
CHKFORTRANNULLINTEGER(gremote);
*ierr = PetscSFSetGraphLayout(
	(PetscSF)PetscToPointer((sf) ),
	(PetscLayout)PetscToPointer((layout) ),*nleaves,ilocal,*localmode,gremote);
}
PETSC_EXTERN void  petscsfsetgraphsection_(PetscSF sf,PetscSection localSection,PetscSection globalSection, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(localSection);
CHKFORTRANNULLOBJECT(globalSection);
*ierr = PetscSFSetGraphSection(
	(PetscSF)PetscToPointer((sf) ),
	(PetscSection)PetscToPointer((localSection) ),
	(PetscSection)PetscToPointer((globalSection) ));
}
PETSC_EXTERN void  petscsfcreatebymatchingindices_(PetscLayout layout,PetscInt *numRootIndices, PetscInt *rootIndices, PetscInt *rootLocalIndices,PetscInt *rootLocalOffset,PetscInt *numLeafIndices, PetscInt *leafIndices, PetscInt *leafLocalIndices,PetscInt *leafLocalOffset,PetscSF *sfA,PetscSF *sf, int *ierr)
{
CHKFORTRANNULLOBJECT(layout);
CHKFORTRANNULLINTEGER(rootIndices);
CHKFORTRANNULLINTEGER(rootLocalIndices);
CHKFORTRANNULLINTEGER(leafIndices);
CHKFORTRANNULLINTEGER(leafLocalIndices);
PetscBool sfA_null = !*(void**) sfA ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfA);
PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
*ierr = PetscSFCreateByMatchingIndices(
	(PetscLayout)PetscToPointer((layout) ),*numRootIndices,rootIndices,rootLocalIndices,*rootLocalOffset,*numLeafIndices,leafIndices,leafLocalIndices,*leafLocalOffset,sfA,sf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfA_null && !*(void**) sfA) * (void **) sfA = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
}
PETSC_EXTERN void  petscsfmerge_(PetscSF sfa,PetscSF sfb,PetscSF *merged, int *ierr)
{
CHKFORTRANNULLOBJECT(sfa);
CHKFORTRANNULLOBJECT(sfb);
PetscBool merged_null = !*(void**) merged ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(merged);
*ierr = PetscSFMerge(
	(PetscSF)PetscToPointer((sfa) ),
	(PetscSF)PetscToPointer((sfb) ),merged);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! merged_null && !*(void**) merged) * (void **) merged = (void *)-2;
}
PETSC_EXTERN void  petscsfcreatestridedsf_(PetscSF sf,PetscInt *bs,PetscInt *ldr,PetscInt *ldl,PetscSF *vsf, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
PetscBool vsf_null = !*(void**) vsf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(vsf);
*ierr = PetscSFCreateStridedSF(
	(PetscSF)PetscToPointer((sf) ),*bs,*ldr,*ldl,vsf);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! vsf_null && !*(void**) vsf) * (void **) vsf = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
