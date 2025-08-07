#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* random.c */
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

#include "petscsys.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomgetvalue_ PETSCRANDOMGETVALUE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomgetvalue_ petscrandomgetvalue
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomgetvaluereal_ PETSCRANDOMGETVALUEREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomgetvaluereal_ petscrandomgetvaluereal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomgetvalues_ PETSCRANDOMGETVALUES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomgetvalues_ petscrandomgetvalues
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomgetvaluesreal_ PETSCRANDOMGETVALUESREAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomgetvaluesreal_ petscrandomgetvaluesreal
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomgetinterval_ PETSCRANDOMGETINTERVAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomgetinterval_ petscrandomgetinterval
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomsetinterval_ PETSCRANDOMSETINTERVAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomsetinterval_ petscrandomsetinterval
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscrandomgetvalue_(PetscRandom r,PetscScalar *val, int *ierr)
{
CHKFORTRANNULLOBJECT(r);
CHKFORTRANNULLSCALAR(val);
*ierr = PetscRandomGetValue(
	(PetscRandom)PetscToPointer((r) ),val);
}
PETSC_EXTERN void  petscrandomgetvaluereal_(PetscRandom r,PetscReal *val, int *ierr)
{
CHKFORTRANNULLOBJECT(r);
CHKFORTRANNULLREAL(val);
*ierr = PetscRandomGetValueReal(
	(PetscRandom)PetscToPointer((r) ),val);
}
PETSC_EXTERN void  petscrandomgetvalues_(PetscRandom r,PetscInt *n,PetscScalar *val, int *ierr)
{
CHKFORTRANNULLOBJECT(r);
CHKFORTRANNULLSCALAR(val);
*ierr = PetscRandomGetValues(
	(PetscRandom)PetscToPointer((r) ),*n,val);
}
PETSC_EXTERN void  petscrandomgetvaluesreal_(PetscRandom r,PetscInt *n,PetscReal *val, int *ierr)
{
CHKFORTRANNULLOBJECT(r);
CHKFORTRANNULLREAL(val);
*ierr = PetscRandomGetValuesReal(
	(PetscRandom)PetscToPointer((r) ),*n,val);
}
PETSC_EXTERN void  petscrandomgetinterval_(PetscRandom r,PetscScalar *low,PetscScalar *high, int *ierr)
{
CHKFORTRANNULLOBJECT(r);
CHKFORTRANNULLSCALAR(low);
CHKFORTRANNULLSCALAR(high);
*ierr = PetscRandomGetInterval(
	(PetscRandom)PetscToPointer((r) ),low,high);
}
PETSC_EXTERN void  petscrandomsetinterval_(PetscRandom r,PetscScalar *low,PetscScalar *high, int *ierr)
{
CHKFORTRANNULLOBJECT(r);
*ierr = PetscRandomSetInterval(
	(PetscRandom)PetscToPointer((r) ),*low,*high);
}
#if defined(__cplusplus)
}
#endif
