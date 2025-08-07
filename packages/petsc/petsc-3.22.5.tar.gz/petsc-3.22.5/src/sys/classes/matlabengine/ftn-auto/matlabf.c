#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* matlab.c */
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

#include "petscmatlab.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmatlabenginecreate_ PETSCMATLABENGINECREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmatlabenginecreate_ petscmatlabenginecreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmatlabenginedestroy_ PETSCMATLABENGINEDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmatlabenginedestroy_ petscmatlabenginedestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmatlabengineput_ PETSCMATLABENGINEPUT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmatlabengineput_ petscmatlabengineput
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmatlabengineget_ PETSCMATLABENGINEGET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmatlabengineget_ petscmatlabengineget
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmatlabengineputarray_ PETSCMATLABENGINEPUTARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmatlabengineputarray_ petscmatlabengineputarray
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscmatlabenginegetarray_ PETSCMATLABENGINEGETARRAY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscmatlabenginegetarray_ petscmatlabenginegetarray
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscmatlabenginecreate_(MPI_Fint * comm, char host[],PetscMatlabEngine *mengine, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool mengine_null = !*(void**) mengine ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mengine);
/* insert Fortran-to-C conversion for host */
  FIXCHAR(host,cl0,_cltmp0);
*ierr = PetscMatlabEngineCreate(
	MPI_Comm_f2c(*(comm)),_cltmp0,mengine);
  FREECHAR(host,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mengine_null && !*(void**) mengine) * (void **) mengine = (void *)-2;
}
PETSC_EXTERN void  petscmatlabenginedestroy_(PetscMatlabEngine *v, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(v);
 PetscBool v_null = !*(void**) v ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(v);
*ierr = PetscMatlabEngineDestroy(v);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! v_null && !*(void**) v) * (void **) v = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(v);
 }
PETSC_EXTERN void  petscmatlabengineput_(PetscMatlabEngine mengine,PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(mengine);
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscMatlabEnginePut(
	(PetscMatlabEngine)PetscToPointer((mengine) ),
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscmatlabengineget_(PetscMatlabEngine mengine,PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(mengine);
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscMatlabEngineGet(
	(PetscMatlabEngine)PetscToPointer((mengine) ),
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscmatlabengineputarray_(PetscMatlabEngine mengine,int *m,int *n, PetscScalar array[], char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mengine);
CHKFORTRANNULLSCALAR(array);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscMatlabEnginePutArray(
	(PetscMatlabEngine)PetscToPointer((mengine) ),*m,*n,array,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscmatlabenginegetarray_(PetscMatlabEngine mengine,int *m,int *n,PetscScalar array[], char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(mengine);
CHKFORTRANNULLSCALAR(array);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscMatlabEngineGetArray(
	(PetscMatlabEngine)PetscToPointer((mengine) ),*m,*n,array,_cltmp0);
  FREECHAR(name,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
