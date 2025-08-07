#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* destroy.c */
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
#define petscobjectdestroy_ PETSCOBJECTDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectdestroy_ petscobjectdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectview_ PETSCOBJECTVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectview_ petscobjectview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectviewfromoptions_ PETSCOBJECTVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectviewfromoptions_ petscobjectviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjecttypecompare_ PETSCOBJECTTYPECOMPARE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjecttypecompare_ petscobjecttypecompare
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectobjecttypecompare_ PETSCOBJECTOBJECTTYPECOMPARE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectobjecttypecompare_ petscobjectobjecttypecompare
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectbasetypecompare_ PETSCOBJECTBASETYPECOMPARE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectbasetypecompare_ petscobjectbasetypecompare
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectregisterdestroy_ PETSCOBJECTREGISTERDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectregisterdestroy_ petscobjectregisterdestroy
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscobjectdestroy_(PetscObject *obj, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(obj);
 PetscBool obj_null = !*(void**) obj ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectDestroy(obj);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! obj_null && !*(void**) obj) * (void **) obj = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(obj);
 }
PETSC_EXTERN void  petscobjectview_(PetscObject obj,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscObjectView(
	(PetscObject)PetscToPointer((obj) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscobjectviewfromoptions_(PetscObject obj,PetscObject bobj, char optionname[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLOBJECT(bobj);
/* insert Fortran-to-C conversion for optionname */
  FIXCHAR(optionname,cl0,_cltmp0);
*ierr = PetscObjectViewFromOptions(
	(PetscObject)PetscToPointer((obj) ),
	(PetscObject)PetscToPointer((bobj) ),_cltmp0);
  FREECHAR(optionname,_cltmp0);
}
PETSC_EXTERN void  petscobjecttypecompare_(PetscObject obj, char type_name[],PetscBool *same, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for type_name */
  FIXCHAR(type_name,cl0,_cltmp0);
*ierr = PetscObjectTypeCompare(
	(PetscObject)PetscToPointer((obj) ),_cltmp0,same);
  FREECHAR(type_name,_cltmp0);
}
PETSC_EXTERN void  petscobjectobjecttypecompare_(PetscObject obj1,PetscObject obj2,PetscBool *same, int *ierr)
{
CHKFORTRANNULLOBJECT(obj1);
CHKFORTRANNULLOBJECT(obj2);
*ierr = PetscObjectObjectTypeCompare(
	(PetscObject)PetscToPointer((obj1) ),
	(PetscObject)PetscToPointer((obj2) ),same);
}
PETSC_EXTERN void  petscobjectbasetypecompare_(PetscObject obj, char type_name[],PetscBool *same, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for type_name */
  FIXCHAR(type_name,cl0,_cltmp0);
*ierr = PetscObjectBaseTypeCompare(
	(PetscObject)PetscToPointer((obj) ),_cltmp0,same);
  FREECHAR(type_name,_cltmp0);
}
PETSC_EXTERN void  petscobjectregisterdestroy_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectRegisterDestroy(
	(PetscObject)PetscToPointer((obj) ));
}
#if defined(__cplusplus)
}
#endif
