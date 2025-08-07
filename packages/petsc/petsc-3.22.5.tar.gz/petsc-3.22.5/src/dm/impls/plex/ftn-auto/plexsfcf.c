#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexsfc.c */
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
#define dmplexsetisoperiodicfacesf_ DMPLEXSETISOPERIODICFACESF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetisoperiodicfacesf_ dmplexsetisoperiodicfacesf
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexsetisoperiodicfacesf_(DM dm,PetscInt *num_face_sfs,PetscSF *face_sfs, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool face_sfs_null = !*(void**) face_sfs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(face_sfs);
*ierr = DMPlexSetIsoperiodicFaceSF(
	(DM)PetscToPointer((dm) ),*num_face_sfs,face_sfs);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! face_sfs_null && !*(void**) face_sfs) * (void **) face_sfs = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
