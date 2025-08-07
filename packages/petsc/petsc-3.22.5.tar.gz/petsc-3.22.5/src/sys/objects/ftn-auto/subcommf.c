#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* subcomm.c */
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
#define petscsubcommsetfromoptions_ PETSCSUBCOMMSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommsetfromoptions_ petscsubcommsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsubcommsetoptionsprefix_ PETSCSUBCOMMSETOPTIONSPREFIX
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommsetoptionsprefix_ petscsubcommsetoptionsprefix
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsubcommview_ PETSCSUBCOMMVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommview_ petscsubcommview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsubcommsetnumber_ PETSCSUBCOMMSETNUMBER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommsetnumber_ petscsubcommsetnumber
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsubcommsettype_ PETSCSUBCOMMSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommsettype_ petscsubcommsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsubcommsettypegeneral_ PETSCSUBCOMMSETTYPEGENERAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommsettypegeneral_ petscsubcommsettypegeneral
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsubcommdestroy_ PETSCSUBCOMMDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommdestroy_ petscsubcommdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscsubcommcreate_ PETSCSUBCOMMCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscsubcommcreate_ petscsubcommcreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscsubcommsetfromoptions_(PetscSubcomm psubcomm, int *ierr)
{
CHKFORTRANNULLOBJECT(psubcomm);
*ierr = PetscSubcommSetFromOptions(
	(PetscSubcomm)PetscToPointer((psubcomm) ));
}
PETSC_EXTERN void  petscsubcommsetoptionsprefix_(PetscSubcomm psubcomm, char pre[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(psubcomm);
/* insert Fortran-to-C conversion for pre */
  FIXCHAR(pre,cl0,_cltmp0);
*ierr = PetscSubcommSetOptionsPrefix(
	(PetscSubcomm)PetscToPointer((psubcomm) ),_cltmp0);
  FREECHAR(pre,_cltmp0);
}
PETSC_EXTERN void  petscsubcommview_(PetscSubcomm psubcomm,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(psubcomm);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscSubcommView(
	(PetscSubcomm)PetscToPointer((psubcomm) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscsubcommsetnumber_(PetscSubcomm psubcomm,PetscInt *nsubcomm, int *ierr)
{
CHKFORTRANNULLOBJECT(psubcomm);
*ierr = PetscSubcommSetNumber(
	(PetscSubcomm)PetscToPointer((psubcomm) ),*nsubcomm);
}
PETSC_EXTERN void  petscsubcommsettype_(PetscSubcomm psubcomm,PetscSubcommType *subcommtype, int *ierr)
{
CHKFORTRANNULLOBJECT(psubcomm);
*ierr = PetscSubcommSetType(
	(PetscSubcomm)PetscToPointer((psubcomm) ),*subcommtype);
}
PETSC_EXTERN void  petscsubcommsettypegeneral_(PetscSubcomm psubcomm,PetscMPIInt *color,PetscMPIInt *subrank, int *ierr)
{
CHKFORTRANNULLOBJECT(psubcomm);
*ierr = PetscSubcommSetTypeGeneral(
	(PetscSubcomm)PetscToPointer((psubcomm) ),*color,*subrank);
}
PETSC_EXTERN void  petscsubcommdestroy_(PetscSubcomm *psubcomm, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(psubcomm);
 PetscBool psubcomm_null = !*(void**) psubcomm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(psubcomm);
*ierr = PetscSubcommDestroy(psubcomm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! psubcomm_null && !*(void**) psubcomm) * (void **) psubcomm = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(psubcomm);
 }
PETSC_EXTERN void  petscsubcommcreate_(MPI_Fint * comm,PetscSubcomm *psubcomm, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(psubcomm);
 PetscBool psubcomm_null = !*(void**) psubcomm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(psubcomm);
*ierr = PetscSubcommCreate(
	MPI_Comm_f2c(*(comm)),psubcomm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! psubcomm_null && !*(void**) psubcomm) * (void **) psubcomm = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
