#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* dmfield.c */
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

#include "petscdmfield.h"
#include "petscdmfield.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfielddestroy_ DMFIELDDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfielddestroy_ dmfielddestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldview_ DMFIELDVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldview_ dmfieldview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldsettype_ DMFIELDSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldsettype_ dmfieldsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldgettype_ DMFIELDGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldgettype_ dmfieldgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldgetnumcomponents_ DMFIELDGETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldgetnumcomponents_ dmfieldgetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldgetdm_ DMFIELDGETDM
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldgetdm_ dmfieldgetdm
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldevaluate_ DMFIELDEVALUATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldevaluate_ dmfieldevaluate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldevaluatefe_ DMFIELDEVALUATEFE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldevaluatefe_ dmfieldevaluatefe
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldevaluatefv_ DMFIELDEVALUATEFV
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldevaluatefv_ dmfieldevaluatefv
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldgetdegree_ DMFIELDGETDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldgetdegree_ dmfieldgetdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmfieldcreatedefaultquadrature_ DMFIELDCREATEDEFAULTQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmfieldcreatedefaultquadrature_ dmfieldcreatedefaultquadrature
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmfielddestroy_(DMField *field, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(field);
 PetscBool field_null = !*(void**) field ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(field);
*ierr = DMFieldDestroy(field);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! field_null && !*(void**) field) * (void **) field = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(field);
 }
PETSC_EXTERN void  dmfieldview_(DMField field,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
CHKFORTRANNULLOBJECT(viewer);
*ierr = DMFieldView(
	(DMField)PetscToPointer((field) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  dmfieldsettype_(DMField field,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(field);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = DMFieldSetType(
	(DMField)PetscToPointer((field) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  dmfieldgettype_(DMField field,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(field);
*ierr = DMFieldGetType(
	(DMField)PetscToPointer((field) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
PETSC_EXTERN void  dmfieldgetnumcomponents_(DMField field,PetscInt *nc, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
CHKFORTRANNULLINTEGER(nc);
*ierr = DMFieldGetNumComponents(
	(DMField)PetscToPointer((field) ),nc);
}
PETSC_EXTERN void  dmfieldgetdm_(DMField field,DM *dm, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
PetscBool dm_null = !*(void**) dm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMFieldGetDM(
	(DMField)PetscToPointer((field) ),dm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dm_null && !*(void**) dm) * (void **) dm = (void *)-2;
}
PETSC_EXTERN void  dmfieldevaluate_(DMField field,Vec points,PetscDataType *datatype,void*B,void*D,void*H, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
CHKFORTRANNULLOBJECT(points);
*ierr = DMFieldEvaluate(
	(DMField)PetscToPointer((field) ),
	(Vec)PetscToPointer((points) ),*datatype,B,D,H);
}
PETSC_EXTERN void  dmfieldevaluatefe_(DMField field,IS cellIS,PetscQuadrature points,PetscDataType *datatype,void*B,void*D,void*H, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
CHKFORTRANNULLOBJECT(cellIS);
CHKFORTRANNULLOBJECT(points);
*ierr = DMFieldEvaluateFE(
	(DMField)PetscToPointer((field) ),
	(IS)PetscToPointer((cellIS) ),
	(PetscQuadrature)PetscToPointer((points) ),*datatype,B,D,H);
}
PETSC_EXTERN void  dmfieldevaluatefv_(DMField field,IS cellIS,PetscDataType *datatype,void*B,void*D,void*H, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
CHKFORTRANNULLOBJECT(cellIS);
*ierr = DMFieldEvaluateFV(
	(DMField)PetscToPointer((field) ),
	(IS)PetscToPointer((cellIS) ),*datatype,B,D,H);
}
PETSC_EXTERN void  dmfieldgetdegree_(DMField field,IS cellIS,PetscInt *minDegree,PetscInt *maxDegree, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
CHKFORTRANNULLOBJECT(cellIS);
CHKFORTRANNULLINTEGER(minDegree);
CHKFORTRANNULLINTEGER(maxDegree);
*ierr = DMFieldGetDegree(
	(DMField)PetscToPointer((field) ),
	(IS)PetscToPointer((cellIS) ),minDegree,maxDegree);
}
PETSC_EXTERN void  dmfieldcreatedefaultquadrature_(DMField field,IS pointIS,PetscQuadrature *quad, int *ierr)
{
CHKFORTRANNULLOBJECT(field);
CHKFORTRANNULLOBJECT(pointIS);
PetscBool quad_null = !*(void**) quad ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(quad);
*ierr = DMFieldCreateDefaultQuadrature(
	(DMField)PetscToPointer((field) ),
	(IS)PetscToPointer((pointIS) ),quad);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! quad_null && !*(void**) quad) * (void **) quad = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
