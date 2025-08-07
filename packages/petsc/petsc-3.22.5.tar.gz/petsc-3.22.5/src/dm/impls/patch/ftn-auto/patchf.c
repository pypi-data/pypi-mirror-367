#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* patch.c */
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

#include "petscdmpatch.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmpatchzoom_ DMPATCHZOOM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmpatchzoom_ dmpatchzoom
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmpatchzoom_(DM dm,MatStencil *lower,MatStencil *upper,MPI_Fint * commz,DM *dmz,PetscSF *sfz,PetscSF *sfzr, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool dmz_null = !*(void**) dmz ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmz);
PetscBool sfz_null = !*(void**) sfz ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfz);
PetscBool sfzr_null = !*(void**) sfzr ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfzr);
*ierr = DMPatchZoom(
	(DM)PetscToPointer((dm) ),*lower,*upper,
	MPI_Comm_f2c(*(commz)),dmz,sfz,sfzr);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmz_null && !*(void**) dmz) * (void **) dmz = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfz_null && !*(void**) sfz) * (void **) sfz = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfzr_null && !*(void**) sfzr) * (void **) sfzr = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
