#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* inherit.c */
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
#define petscobjectcopyfortranfunctionpointers_ PETSCOBJECTCOPYFORTRANFUNCTIONPOINTERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectcopyfortranfunctionpointers_ petscobjectcopyfortranfunctionpointers
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsview_ PETSCOBJECTSVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsview_ petscobjectsview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsgetobject_ PETSCOBJECTSGETOBJECT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsgetobject_ petscobjectsgetobject
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsetprintedoptions_ PETSCOBJECTSETPRINTEDOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsetprintedoptions_ petscobjectsetprintedoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectinheritprintedoptions_ PETSCOBJECTINHERITPRINTEDOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectinheritprintedoptions_ petscobjectinheritprintedoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectdestroyoptionshandlers_ PETSCOBJECTDESTROYOPTIONSHANDLERS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectdestroyoptionshandlers_ petscobjectdestroyoptionshandlers
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectreference_ PETSCOBJECTREFERENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectreference_ petscobjectreference
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectgetreference_ PETSCOBJECTGETREFERENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectgetreference_ petscobjectgetreference
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectdereference_ PETSCOBJECTDEREFERENCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectdereference_ petscobjectdereference
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectcompose_ PETSCOBJECTCOMPOSE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectcompose_ petscobjectcompose
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectquery_ PETSCOBJECTQUERY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectquery_ petscobjectquery
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsetfromoptions_ PETSCOBJECTSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsetfromoptions_ petscobjectsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscobjectsetup_ PETSCOBJECTSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscobjectsetup_ petscobjectsetup
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscobjectcopyfortranfunctionpointers_(PetscObject src,PetscObject dest, int *ierr)
{
CHKFORTRANNULLOBJECT(src);
CHKFORTRANNULLOBJECT(dest);
*ierr = PetscObjectCopyFortranFunctionPointers(
	(PetscObject)PetscToPointer((src) ),
	(PetscObject)PetscToPointer((dest) ));
}
PETSC_EXTERN void  petscobjectsview_(PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscObjectsView(PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscobjectsgetobject_( char name[],PetscObject *obj, char *classname, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0, PETSC_FORTRAN_CHARLEN_T cl1)
{
  char *_cltmp0 = PETSC_NULLPTR;
  char *_cltmp1 = PETSC_NULLPTR;
PetscBool obj_null = !*(void**) obj ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscObjectsGetObject(_cltmp0,obj,(const char **)&_cltmp1);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! obj_null && !*(void**) obj) * (void **) obj = (void *)-2;
/* insert C-to-Fortran conversion for classname */
*ierr = PetscStrncpy(classname, _cltmp1, cl1);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, classname, cl1);
}
PETSC_EXTERN void  petscobjectsetprintedoptions_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectSetPrintedOptions(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectinheritprintedoptions_(PetscObject pobj,PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(pobj);
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectInheritPrintedOptions(
	(PetscObject)PetscToPointer((pobj) ),
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectdestroyoptionshandlers_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectDestroyOptionsHandlers(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectreference_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectReference(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectgetreference_(PetscObject obj,PetscInt *cnt, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLINTEGER(cnt);
*ierr = PetscObjectGetReference(
	(PetscObject)PetscToPointer((obj) ),cnt);
}
PETSC_EXTERN void  petscobjectdereference_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectDereference(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectcompose_(PetscObject obj, char name[],PetscObject ptr, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
CHKFORTRANNULLOBJECT(ptr);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscObjectCompose(
	(PetscObject)PetscToPointer((obj) ),_cltmp0,
	(PetscObject)PetscToPointer((ptr) ));
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscobjectquery_(PetscObject obj, char name[],PetscObject *ptr, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(obj);
PetscBool ptr_null = !*(void**) ptr ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ptr);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscObjectQuery(
	(PetscObject)PetscToPointer((obj) ),_cltmp0,ptr);
  FREECHAR(name,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ptr_null && !*(void**) ptr) * (void **) ptr = (void *)-2;
}
PETSC_EXTERN void  petscobjectsetfromoptions_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectSetFromOptions(
	(PetscObject)PetscToPointer((obj) ));
}
PETSC_EXTERN void  petscobjectsetup_(PetscObject obj, int *ierr)
{
CHKFORTRANNULLOBJECT(obj);
*ierr = PetscObjectSetUp(
	(PetscObject)PetscToPointer((obj) ));
}
#if defined(__cplusplus)
}
#endif
