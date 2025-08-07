#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* space.c */
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

#include "petscfe.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacesettype_ PETSCSPACESETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacesettype_ petscspacesettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacegettype_ PETSCSPACEGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacegettype_ petscspacegettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspaceviewfromoptions_ PETSCSPACEVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspaceviewfromoptions_ petscspaceviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspaceview_ PETSCSPACEVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspaceview_ petscspaceview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacesetfromoptions_ PETSCSPACESETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacesetfromoptions_ petscspacesetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacesetup_ PETSCSPACESETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacesetup_ petscspacesetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacedestroy_ PETSCSPACEDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacedestroy_ petscspacedestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacecreate_ PETSCSPACECREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacecreate_ petscspacecreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacegetdimension_ PETSCSPACEGETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacegetdimension_ petscspacegetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacegetdegree_ PETSCSPACEGETDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacegetdegree_ petscspacegetdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacesetdegree_ PETSCSPACESETDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacesetdegree_ petscspacesetdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacegetnumcomponents_ PETSCSPACEGETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacegetnumcomponents_ petscspacegetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacesetnumcomponents_ PETSCSPACESETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacesetnumcomponents_ petscspacesetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacesetnumvariables_ PETSCSPACESETNUMVARIABLES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacesetnumvariables_ petscspacesetnumvariables
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacegetnumvariables_ PETSCSPACEGETNUMVARIABLES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacegetnumvariables_ petscspacegetnumvariables
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspaceevaluate_ PETSCSPACEEVALUATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspaceevaluate_ petscspaceevaluate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscspacegetheightsubspace_ PETSCSPACEGETHEIGHTSUBSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscspacegetheightsubspace_ petscspacegetheightsubspace
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscspacesettype_(PetscSpace sp,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(sp);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscSpaceSetType(
	(PetscSpace)PetscToPointer((sp) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscspacegettype_(PetscSpace sp,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceGetType(
	(PetscSpace)PetscToPointer((sp) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscspaceviewfromoptions_(PetscSpace A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscSpaceViewFromOptions(
	(PetscSpace)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscspaceview_(PetscSpace sp,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscSpaceView(
	(PetscSpace)PetscToPointer((sp) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  petscspacesetfromoptions_(PetscSpace sp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceSetFromOptions(
	(PetscSpace)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscspacesetup_(PetscSpace sp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceSetUp(
	(PetscSpace)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscspacedestroy_(PetscSpace *sp, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(sp);
 PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceDestroy(sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(sp);
 }
PETSC_EXTERN void  petscspacecreate_(MPI_Fint * comm,PetscSpace *sp, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(sp);
 PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceCreate(
	MPI_Comm_f2c(*(comm)),sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  petscspacegetdimension_(PetscSpace sp,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscSpaceGetDimension(
	(PetscSpace)PetscToPointer((sp) ),dim);
}
PETSC_EXTERN void  petscspacegetdegree_(PetscSpace sp,PetscInt *minDegree,PetscInt *maxDegree, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(minDegree);
CHKFORTRANNULLINTEGER(maxDegree);
*ierr = PetscSpaceGetDegree(
	(PetscSpace)PetscToPointer((sp) ),minDegree,maxDegree);
}
PETSC_EXTERN void  petscspacesetdegree_(PetscSpace sp,PetscInt *degree,PetscInt *maxDegree, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceSetDegree(
	(PetscSpace)PetscToPointer((sp) ),*degree,*maxDegree);
}
PETSC_EXTERN void  petscspacegetnumcomponents_(PetscSpace sp,PetscInt *Nc, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(Nc);
*ierr = PetscSpaceGetNumComponents(
	(PetscSpace)PetscToPointer((sp) ),Nc);
}
PETSC_EXTERN void  petscspacesetnumcomponents_(PetscSpace sp,PetscInt *Nc, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceSetNumComponents(
	(PetscSpace)PetscToPointer((sp) ),*Nc);
}
PETSC_EXTERN void  petscspacesetnumvariables_(PetscSpace sp,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscSpaceSetNumVariables(
	(PetscSpace)PetscToPointer((sp) ),*n);
}
PETSC_EXTERN void  petscspacegetnumvariables_(PetscSpace sp,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLINTEGER(n);
*ierr = PetscSpaceGetNumVariables(
	(PetscSpace)PetscToPointer((sp) ),n);
}
PETSC_EXTERN void  petscspaceevaluate_(PetscSpace sp,PetscInt *npoints, PetscReal points[],PetscReal B[],PetscReal D[],PetscReal H[], int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
CHKFORTRANNULLREAL(points);
CHKFORTRANNULLREAL(B);
CHKFORTRANNULLREAL(D);
CHKFORTRANNULLREAL(H);
*ierr = PetscSpaceEvaluate(
	(PetscSpace)PetscToPointer((sp) ),*npoints,points,B,D,H);
}
PETSC_EXTERN void  petscspacegetheightsubspace_(PetscSpace sp,PetscInt *height,PetscSpace *subsp, int *ierr)
{
CHKFORTRANNULLOBJECT(sp);
PetscBool subsp_null = !*(void**) subsp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subsp);
*ierr = PetscSpaceGetHeightSubspace(
	(PetscSpace)PetscToPointer((sp) ),*height,subsp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subsp_null && !*(void**) subsp) * (void **) subsp = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
