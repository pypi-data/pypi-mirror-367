#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* snesmfj2.c */
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

#include "petscsnes.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatesnesmfmore_ MATCREATESNESMFMORE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatesnesmfmore_ matcreatesnesmfmore
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matsnesmfmoresetparameters_ MATSNESMFMORESETPARAMETERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matsnesmfmoresetparameters_ matsnesmfmoresetparameters
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matcreatesnesmfmore_(SNES snes,Vec x,Mat *J, int *ierr)
{
CHKFORTRANNULLOBJECT(snes);
CHKFORTRANNULLOBJECT(x);
PetscBool J_null = !*(void**) J ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(J);
*ierr = MatCreateSNESMFMore(
	(SNES)PetscToPointer((snes) ),
	(Vec)PetscToPointer((x) ),J);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! J_null && !*(void**) J) * (void **) J = (void *)-2;
}
PETSC_EXTERN void  matsnesmfmoresetparameters_(Mat mat,PetscReal *error,PetscReal *umin,PetscReal *h, int *ierr)
{
CHKFORTRANNULLOBJECT(mat);
*ierr = MatSNESMFMoreSetParameters(
	(Mat)PetscToPointer((mat) ),*error,*umin,*h);
}
#if defined(__cplusplus)
}
#endif
