#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fv.c */
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

#include "petscfv.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimitersettype_ PETSCLIMITERSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimitersettype_ petsclimitersettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimitergettype_ PETSCLIMITERGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimitergettype_ petsclimitergettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimiterviewfromoptions_ PETSCLIMITERVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimiterviewfromoptions_ petsclimiterviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimiterview_ PETSCLIMITERVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimiterview_ petsclimiterview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimitersetfromoptions_ PETSCLIMITERSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimitersetfromoptions_ petsclimitersetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimitersetup_ PETSCLIMITERSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimitersetup_ petsclimitersetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimiterdestroy_ PETSCLIMITERDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimiterdestroy_ petsclimiterdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimitercreate_ PETSCLIMITERCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimitercreate_ petsclimitercreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsclimiterlimit_ PETSCLIMITERLIMIT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsclimiterlimit_ petsclimiterlimit
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsettype_ PETSCFVSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsettype_ petscfvsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgettype_ PETSCFVGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgettype_ petscfvgettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvviewfromoptions_ PETSCFVVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvviewfromoptions_ petscfvviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvview_ PETSCFVVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvview_ petscfvview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetfromoptions_ PETSCFVSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetfromoptions_ petscfvsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetup_ PETSCFVSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetup_ petscfvsetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvdestroy_ PETSCFVDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvdestroy_ petscfvdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvcreate_ PETSCFVCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvcreate_ petscfvcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetlimiter_ PETSCFVSETLIMITER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetlimiter_ petscfvsetlimiter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgetlimiter_ PETSCFVGETLIMITER
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgetlimiter_ petscfvgetlimiter
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetnumcomponents_ PETSCFVSETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetnumcomponents_ petscfvsetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgetnumcomponents_ PETSCFVGETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgetnumcomponents_ petscfvgetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetcomponentname_ PETSCFVSETCOMPONENTNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetcomponentname_ petscfvsetcomponentname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgetcomponentname_ PETSCFVGETCOMPONENTNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgetcomponentname_ petscfvgetcomponentname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetspatialdimension_ PETSCFVSETSPATIALDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetspatialdimension_ petscfvsetspatialdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgetspatialdimension_ PETSCFVGETSPATIALDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgetspatialdimension_ petscfvgetspatialdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetcomputegradients_ PETSCFVSETCOMPUTEGRADIENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetcomputegradients_ petscfvsetcomputegradients
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgetcomputegradients_ PETSCFVGETCOMPUTEGRADIENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgetcomputegradients_ petscfvgetcomputegradients
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetquadrature_ PETSCFVSETQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetquadrature_ petscfvsetquadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgetquadrature_ PETSCFVGETQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgetquadrature_ petscfvgetquadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvcreatedualspace_ PETSCFVCREATEDUALSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvcreatedualspace_ petscfvcreatedualspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvgetdualspace_ PETSCFVGETDUALSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvgetdualspace_ petscfvgetdualspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvsetdualspace_ PETSCFVSETDUALSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvsetdualspace_ petscfvsetdualspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvcomputegradient_ PETSCFVCOMPUTEGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvcomputegradient_ petscfvcomputegradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvclone_ PETSCFVCLONE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvclone_ petscfvclone
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvrefine_ PETSCFVREFINE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvrefine_ petscfvrefine
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfvleastsquaressetmaxfaces_ PETSCFVLEASTSQUARESSETMAXFACES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfvleastsquaressetmaxfaces_ petscfvleastsquaressetmaxfaces
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petsclimitersettype_(PetscLimiter lim,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(lim);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLimiterSetType(
	(PetscLimiter)PetscToPointer((lim) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclimitergettype_(PetscLimiter lim,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(lim);
*ierr = PetscLimiterGetType(
	(PetscLimiter)PetscToPointer((lim) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petsclimiterviewfromoptions_(PetscLimiter A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscLimiterViewFromOptions(
	(PetscLimiter)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petsclimiterview_(PetscLimiter lim,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(lim);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscLimiterView(
	(PetscLimiter)PetscToPointer((lim) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  petsclimitersetfromoptions_(PetscLimiter lim, int *ierr)
{
CHKFORTRANNULLOBJECT(lim);
*ierr = PetscLimiterSetFromOptions(
	(PetscLimiter)PetscToPointer((lim) ));
}
PETSC_EXTERN void  petsclimitersetup_(PetscLimiter lim, int *ierr)
{
CHKFORTRANNULLOBJECT(lim);
*ierr = PetscLimiterSetUp(
	(PetscLimiter)PetscToPointer((lim) ));
}
PETSC_EXTERN void  petsclimiterdestroy_(PetscLimiter *lim, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(lim);
 PetscBool lim_null = !*(void**) lim ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lim);
*ierr = PetscLimiterDestroy(lim);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lim_null && !*(void**) lim) * (void **) lim = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(lim);
 }
PETSC_EXTERN void  petsclimitercreate_(MPI_Fint * comm,PetscLimiter *lim, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(lim);
 PetscBool lim_null = !*(void**) lim ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lim);
*ierr = PetscLimiterCreate(
	MPI_Comm_f2c(*(comm)),lim);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lim_null && !*(void**) lim) * (void **) lim = (void *)-2;
}
PETSC_EXTERN void  petsclimiterlimit_(PetscLimiter lim,PetscReal *flim,PetscReal *phi, int *ierr)
{
CHKFORTRANNULLOBJECT(lim);
CHKFORTRANNULLREAL(phi);
*ierr = PetscLimiterLimit(
	(PetscLimiter)PetscToPointer((lim) ),*flim,phi);
}
PETSC_EXTERN void  petscfvsettype_(PetscFV fvm,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(fvm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscFVSetType(
	(PetscFV)PetscToPointer((fvm) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscfvgettype_(PetscFV fvm,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVGetType(
	(PetscFV)PetscToPointer((fvm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscfvviewfromoptions_(PetscFV A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscFVViewFromOptions(
	(PetscFV)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscfvview_(PetscFV fvm,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscFVView(
	(PetscFV)PetscToPointer((fvm) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  petscfvsetfromoptions_(PetscFV fvm, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVSetFromOptions(
	(PetscFV)PetscToPointer((fvm) ));
}
PETSC_EXTERN void  petscfvsetup_(PetscFV fvm, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVSetUp(
	(PetscFV)PetscToPointer((fvm) ));
}
PETSC_EXTERN void  petscfvdestroy_(PetscFV *fvm, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(fvm);
 PetscBool fvm_null = !*(void**) fvm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVDestroy(fvm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fvm_null && !*(void**) fvm) * (void **) fvm = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(fvm);
 }
PETSC_EXTERN void  petscfvcreate_(MPI_Fint * comm,PetscFV *fvm, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(fvm);
 PetscBool fvm_null = !*(void**) fvm ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVCreate(
	MPI_Comm_f2c(*(comm)),fvm);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fvm_null && !*(void**) fvm) * (void **) fvm = (void *)-2;
}
PETSC_EXTERN void  petscfvsetlimiter_(PetscFV fvm,PetscLimiter lim, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLOBJECT(lim);
*ierr = PetscFVSetLimiter(
	(PetscFV)PetscToPointer((fvm) ),
	(PetscLimiter)PetscToPointer((lim) ));
}
PETSC_EXTERN void  petscfvgetlimiter_(PetscFV fvm,PetscLimiter *lim, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
PetscBool lim_null = !*(void**) lim ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(lim);
*ierr = PetscFVGetLimiter(
	(PetscFV)PetscToPointer((fvm) ),lim);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! lim_null && !*(void**) lim) * (void **) lim = (void *)-2;
}
PETSC_EXTERN void  petscfvsetnumcomponents_(PetscFV fvm,PetscInt *comp, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVSetNumComponents(
	(PetscFV)PetscToPointer((fvm) ),*comp);
}
PETSC_EXTERN void  petscfvgetnumcomponents_(PetscFV fvm,PetscInt *comp, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLINTEGER(comp);
*ierr = PetscFVGetNumComponents(
	(PetscFV)PetscToPointer((fvm) ),comp);
}
PETSC_EXTERN void  petscfvsetcomponentname_(PetscFV fvm,PetscInt *comp, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(fvm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscFVSetComponentName(
	(PetscFV)PetscToPointer((fvm) ),*comp,_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscfvgetcomponentname_(PetscFV fvm,PetscInt *comp, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVGetComponentName(
	(PetscFV)PetscToPointer((fvm) ),*comp,(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscfvsetspatialdimension_(PetscFV fvm,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVSetSpatialDimension(
	(PetscFV)PetscToPointer((fvm) ),*dim);
}
PETSC_EXTERN void  petscfvgetspatialdimension_(PetscFV fvm,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscFVGetSpatialDimension(
	(PetscFV)PetscToPointer((fvm) ),dim);
}
PETSC_EXTERN void  petscfvsetcomputegradients_(PetscFV fvm,PetscBool *computeGradients, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVSetComputeGradients(
	(PetscFV)PetscToPointer((fvm) ),*computeGradients);
}
PETSC_EXTERN void  petscfvgetcomputegradients_(PetscFV fvm,PetscBool *computeGradients, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVGetComputeGradients(
	(PetscFV)PetscToPointer((fvm) ),computeGradients);
}
PETSC_EXTERN void  petscfvsetquadrature_(PetscFV fvm,PetscQuadrature q, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLOBJECT(q);
*ierr = PetscFVSetQuadrature(
	(PetscFV)PetscToPointer((fvm) ),
	(PetscQuadrature)PetscToPointer((q) ));
}
PETSC_EXTERN void  petscfvgetquadrature_(PetscFV fvm,PetscQuadrature *q, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
PetscBool q_null = !*(void**) q ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(q);
*ierr = PetscFVGetQuadrature(
	(PetscFV)PetscToPointer((fvm) ),q);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! q_null && !*(void**) q) * (void **) q = (void *)-2;
}
PETSC_EXTERN void  petscfvcreatedualspace_(PetscFV fvm,DMPolytopeType *ct, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVCreateDualSpace(
	(PetscFV)PetscToPointer((fvm) ),*ct);
}
PETSC_EXTERN void  petscfvgetdualspace_(PetscFV fvm,PetscDualSpace *sp, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscFVGetDualSpace(
	(PetscFV)PetscToPointer((fvm) ),sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  petscfvsetdualspace_(PetscFV fvm,PetscDualSpace sp, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscFVSetDualSpace(
	(PetscFV)PetscToPointer((fvm) ),
	(PetscDualSpace)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscfvcomputegradient_(PetscFV fvm,PetscInt *numFaces,PetscScalar dx[],PetscScalar grad[], int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
CHKFORTRANNULLSCALAR(dx);
CHKFORTRANNULLSCALAR(grad);
*ierr = PetscFVComputeGradient(
	(PetscFV)PetscToPointer((fvm) ),*numFaces,dx,grad);
}
PETSC_EXTERN void  petscfvclone_(PetscFV fv,PetscFV *fvNew, int *ierr)
{
CHKFORTRANNULLOBJECT(fv);
PetscBool fvNew_null = !*(void**) fvNew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fvNew);
*ierr = PetscFVClone(
	(PetscFV)PetscToPointer((fv) ),fvNew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fvNew_null && !*(void**) fvNew) * (void **) fvNew = (void *)-2;
}
PETSC_EXTERN void  petscfvrefine_(PetscFV fv,PetscFV *fvRef, int *ierr)
{
CHKFORTRANNULLOBJECT(fv);
PetscBool fvRef_null = !*(void**) fvRef ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fvRef);
*ierr = PetscFVRefine(
	(PetscFV)PetscToPointer((fv) ),fvRef);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fvRef_null && !*(void**) fvRef) * (void **) fvRef = (void *)-2;
}
PETSC_EXTERN void  petscfvleastsquaressetmaxfaces_(PetscFV fvm,PetscInt *maxFaces, int *ierr)
{
CHKFORTRANNULLOBJECT(fvm);
*ierr = PetscFVLeastSquaresSetMaxFaces(
	(PetscFV)PetscToPointer((fvm) ),*maxFaces);
}
#if defined(__cplusplus)
}
#endif
