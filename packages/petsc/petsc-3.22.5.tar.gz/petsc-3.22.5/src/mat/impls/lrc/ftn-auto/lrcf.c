#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* lrc.c */
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

#include "petscmat.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matlrcgetmats_ MATLRCGETMATS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matlrcgetmats_ matlrcgetmats
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matlrcsetmats_ MATLRCSETMATS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matlrcsetmats_ matlrcsetmats
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define matcreatelrc_ MATCREATELRC
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define matcreatelrc_ matcreatelrc
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  matlrcgetmats_(Mat N,Mat *A,Mat *U,Vec *c,Mat *V, int *ierr)
{
CHKFORTRANNULLOBJECT(N);
PetscBool A_null = !*(void**) A ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(A);
PetscBool U_null = !*(void**) U ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(U);
PetscBool c_null = !*(void**) c ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(c);
PetscBool V_null = !*(void**) V ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(V);
*ierr = MatLRCGetMats(
	(Mat)PetscToPointer((N) ),A,U,c,V);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! A_null && !*(void**) A) * (void **) A = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! U_null && !*(void**) U) * (void **) U = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! c_null && !*(void**) c) * (void **) c = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! V_null && !*(void**) V) * (void **) V = (void *)-2;
}
PETSC_EXTERN void  matlrcsetmats_(Mat N,Mat A,Mat U,Vec c,Mat V, int *ierr)
{
CHKFORTRANNULLOBJECT(N);
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(c);
CHKFORTRANNULLOBJECT(V);
*ierr = MatLRCSetMats(
	(Mat)PetscToPointer((N) ),
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((U) ),
	(Vec)PetscToPointer((c) ),
	(Mat)PetscToPointer((V) ));
}
PETSC_EXTERN void  matcreatelrc_(Mat A,Mat U,Vec c,Mat V,Mat *N, int *ierr)
{
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(U);
CHKFORTRANNULLOBJECT(c);
CHKFORTRANNULLOBJECT(V);
PetscBool N_null = !*(void**) N ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(N);
*ierr = MatCreateLRC(
	(Mat)PetscToPointer((A) ),
	(Mat)PetscToPointer((U) ),
	(Vec)PetscToPointer((c) ),
	(Mat)PetscToPointer((V) ),N);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! N_null && !*(void**) N) * (void **) N = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
