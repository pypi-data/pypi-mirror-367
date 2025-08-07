#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* bm.c */
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

#include "petscbm.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchreset_ PETSCBENCHRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchreset_ petscbenchreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchdestroy_ PETSCBENCHDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchdestroy_ petscbenchdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchsetup_ PETSCBENCHSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchsetup_ petscbenchsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchrun_ PETSCBENCHRUN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchrun_ petscbenchrun
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchsetfromoptions_ PETSCBENCHSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchsetfromoptions_ petscbenchsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchview_ PETSCBENCHVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchview_ petscbenchview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchviewfromoptions_ PETSCBENCHVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchviewfromoptions_ petscbenchviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchcreate_ PETSCBENCHCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchcreate_ petscbenchcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchsetoptionsprefix_ PETSCBENCHSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchsetoptionsprefix_ petscbenchsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchsetsize_ PETSCBENCHSETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchsetsize_ petscbenchsetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchgetsize_ PETSCBENCHGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchgetsize_ petscbenchgetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchsettype_ PETSCBENCHSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchsettype_ petscbenchsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscbenchgettype_ PETSCBENCHGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscbenchgettype_ petscbenchgettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscbenchreset_(PetscBench bm, int *ierr)
{
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchReset(
	(PetscBench)PetscToPointer((bm) ));
}
PETSC_EXTERN void  petscbenchdestroy_(PetscBench *bm, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(bm);
 PetscBool bm_null = !*(void**) bm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchDestroy(bm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! bm_null && !*(void**) bm) * (void **) bm = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(bm);
 }
PETSC_EXTERN void  petscbenchsetup_(PetscBench bm, int *ierr)
{
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchSetUp(
	(PetscBench)PetscToPointer((bm) ));
}
PETSC_EXTERN void  petscbenchrun_(PetscBench bm, int *ierr)
{
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchRun(
	(PetscBench)PetscToPointer((bm) ));
}
PETSC_EXTERN void  petscbenchsetfromoptions_(PetscBench bm, int *ierr)
{
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchSetFromOptions(
	(PetscBench)PetscToPointer((bm) ));
}
PETSC_EXTERN void  petscbenchview_(PetscBench bm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(bm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscBenchView(
	(PetscBench)PetscToPointer((bm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscbenchviewfromoptions_(PetscBench bm,PetscObject bobj, char optionname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(bm);
CHKFORTRANNULLOBJECT(bobj);
/* insert Fortran-to-C conversion for optionname */
  FIXCHAR(optionname,cl0,_cltmp0);
*ierr = PetscBenchViewFromOptions(
	(PetscBench)PetscToPointer((bm) ),
	(PetscObject)PetscToPointer((bobj) ),_cltmp0);
  FREECHAR(optionname,_cltmp0);
}
PETSC_EXTERN void  petscbenchcreate_(MPI_Fint * comm,PetscBench *bm, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(bm);
 PetscBool bm_null = !*(void**) bm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchCreate(
	MPI_Comm_f2c(*(comm)),bm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! bm_null && !*(void**) bm) * (void **) bm = (void *)-2;
}
PETSC_EXTERN void  petscbenchsetoptionsprefix_(PetscBench bm, char pre[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(bm);
/* insert Fortran-to-C conversion for pre */
  FIXCHAR(pre,cl0,_cltmp0);
*ierr = PetscBenchSetOptionsPrefix(
	(PetscBench)PetscToPointer((bm) ),_cltmp0);
  FREECHAR(pre,_cltmp0);
}
PETSC_EXTERN void  petscbenchsetsize_(PetscBench bm,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchSetSize(
	(PetscBench)PetscToPointer((bm) ),*n);
}
PETSC_EXTERN void  petscbenchgetsize_(PetscBench bm,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(bm);
CHKFORTRANNULLINTEGER(n);
*ierr = PetscBenchGetSize(
	(PetscBench)PetscToPointer((bm) ),n);
}
PETSC_EXTERN void  petscbenchsettype_(PetscBench bm,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(bm);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = PetscBenchSetType(
	(PetscBench)PetscToPointer((bm) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  petscbenchgettype_(PetscBench bm,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(bm);
*ierr = PetscBenchGetType(
	(PetscBench)PetscToPointer((bm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
#if defined(__cplusplus)
}
#endif
