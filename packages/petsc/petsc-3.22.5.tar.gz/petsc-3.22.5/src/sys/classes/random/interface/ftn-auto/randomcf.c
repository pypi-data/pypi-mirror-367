#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* randomc.c */
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
#define petscrandomdestroy_ PETSCRANDOMDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomdestroy_ petscrandomdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomsetfromoptions_ PETSCRANDOMSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomsetfromoptions_ petscrandomsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomsetoptionsprefix_ PETSCRANDOMSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomsetoptionsprefix_ petscrandomsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomviewfromoptions_ PETSCRANDOMVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomviewfromoptions_ petscrandomviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomview_ PETSCRANDOMVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomview_ petscrandomview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomcreate_ PETSCRANDOMCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomcreate_ petscrandomcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscrandomseed_ PETSCRANDOMSEED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscrandomseed_ petscrandomseed
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscrandomdestroy_(PetscRandom *r, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(r);
 PetscBool r_null = !*(void**) r ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(r);
*ierr = PetscRandomDestroy(r);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! r_null && !*(void**) r) * (void **) r = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(r);
 }
PETSC_EXTERN void  petscrandomsetfromoptions_(PetscRandom rnd, int *ierr)
{
CHKFORTRANNULLOBJECT(rnd);
*ierr = PetscRandomSetFromOptions(
	(PetscRandom)PetscToPointer((rnd) ));
}
PETSC_EXTERN void  petscrandomsetoptionsprefix_(PetscRandom r, char prefix[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(r);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscRandomSetOptionsPrefix(
	(PetscRandom)PetscToPointer((r) ),_cltmp0);
  FREECHAR(prefix,_cltmp0);
}
PETSC_EXTERN void  petscrandomviewfromoptions_(PetscRandom A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscRandomViewFromOptions(
	(PetscRandom)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscrandomview_(PetscRandom rnd,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(rnd);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscRandomView(
	(PetscRandom)PetscToPointer((rnd) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscrandomcreate_(MPI_Fint * comm,PetscRandom *r, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(r);
 PetscBool r_null = !*(void**) r ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(r);
*ierr = PetscRandomCreate(
	MPI_Comm_f2c(*(comm)),r);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! r_null && !*(void**) r) * (void **) r = (void *)-2;
}
PETSC_EXTERN void  petscrandomseed_(PetscRandom r, int *ierr)
{
CHKFORTRANNULLOBJECT(r);
*ierr = PetscRandomSeed(
	(PetscRandom)PetscToPointer((r) ));
}
#if defined(__cplusplus)
}
#endif
